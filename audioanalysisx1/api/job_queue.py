"""
Job Queue
=========

Async job queue for managing analysis tasks.
"""

import asyncio
from typing import Dict, Optional, List
from datetime import datetime
from collections import defaultdict
import logging

from .models import AnalysisStatus, AnalysisResponse

logger = logging.getLogger(__name__)


class JobQueue:
    """Async job queue manager."""

    def __init__(self, max_workers: int = 4):
        """
        Initialize job queue.

        Args:
            max_workers: Maximum concurrent jobs
        """
        self.max_workers = max_workers
        self.jobs: Dict[str, AnalysisResponse] = {}
        self.job_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

        logger.info(f"Initialized job queue with {max_workers} workers")

    async def create_job(
        self,
        job_id: str,
        audio_path: str,
        asset_id: Optional[str] = None
    ) -> AnalysisResponse:
        """
        Create a new job.

        Args:
            job_id: Unique job identifier
            audio_path: Path to audio file
            asset_id: Optional asset identifier

        Returns:
            AnalysisResponse object
        """
        job = AnalysisResponse(
            job_id=job_id,
            status=AnalysisStatus.PENDING,
            created_at=datetime.utcnow()
        )

        async with self.job_locks[job_id]:
            self.jobs[job_id] = job

        logger.info(f"Created job {job_id}")
        return job

    async def get_job(self, job_id: str) -> Optional[AnalysisResponse]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            AnalysisResponse or None if not found
        """
        return self.jobs.get(job_id)

    async def update_job(self, job_id: str, status: AnalysisStatus):
        """
        Update job status.

        Args:
            job_id: Job identifier
            status: New status
        """
        async with self.job_locks[job_id]:
            if job_id in self.jobs:
                self.jobs[job_id].status = status
                logger.debug(f"Updated job {job_id} status to {status}")

    async def complete_job(self, job_id: str, result: Dict):
        """
        Mark job as completed with results.

        Args:
            job_id: Job identifier
            result: Analysis results
        """
        async with self.job_locks[job_id]:
            if job_id in self.jobs:
                self.jobs[job_id].status = AnalysisStatus.COMPLETED
                self.jobs[job_id].result = result
                self.jobs[job_id].completed_at = datetime.utcnow()
                logger.info(f"Completed job {job_id}")

    async def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed.

        Args:
            job_id: Job identifier
            error: Error message
        """
        async with self.job_locks[job_id]:
            if job_id in self.jobs:
                self.jobs[job_id].status = AnalysisStatus.FAILED
                self.jobs[job_id].error = error
                self.jobs[job_id].completed_at = datetime.utcnow()
                logger.error(f"Failed job {job_id}: {error}")

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled, False if not found or already completed
        """
        async with self.job_locks[job_id]:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                if job.status in [AnalysisStatus.PENDING, AnalysisStatus.PROCESSING]:
                    job.status = AnalysisStatus.FAILED
                    job.error = "Cancelled by user"
                    job.completed_at = datetime.utcnow()
                    logger.info(f"Cancelled job {job_id}")
                    return True
        return False

    async def list_jobs(
        self,
        status: Optional[AnalysisStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AnalysisResponse]:
        """
        List jobs with optional filtering.

        Args:
            status: Filter by status
            limit: Maximum results
            offset: Result offset

        Returns:
            List of AnalysisResponse objects
        """
        jobs = list(self.jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by creation time (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        return jobs[offset:offset + limit]

    def get_active_count(self) -> int:
        """Get count of active (pending/processing) jobs."""
        return sum(
            1 for job in self.jobs.values()
            if job.status in [AnalysisStatus.PENDING, AnalysisStatus.PROCESSING]
        )

    def update_max_workers(self, max_workers: int):
        """Update maximum concurrent workers."""
        self.max_workers = max_workers
        logger.info(f"Updated max workers to {max_workers}")

    async def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up old completed jobs.

        Args:
            max_age_hours: Maximum age in hours
        """
        now = datetime.utcnow()
        to_remove = []

        for job_id, job in self.jobs.items():
            if job.completed_at:
                age = (now - job.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(job_id)

        for job_id in to_remove:
            async with self.job_locks[job_id]:
                del self.jobs[job_id]
                if job_id in self.job_locks:
                    del self.job_locks[job_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old jobs")
