"""
Result Storage
==============

Storage backend for analysis results.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ResultStorage:
    """Storage manager for analysis results."""

    def __init__(self, base_path: str = "./api_results"):
        """
        Initialize storage.

        Args:
            base_path: Base directory for storing results
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized result storage at {self.base_path}")

    def get_job_dir(self, job_id: str) -> Path:
        """
        Get directory for job results.

        Args:
            job_id: Job identifier

        Returns:
            Path to job directory
        """
        job_dir = self.base_path / job_id
        job_dir.mkdir(exist_ok=True)
        return job_dir

    async def store_result(self, job_id: str, result: Dict[str, Any]):
        """
        Store analysis result.

        Args:
            job_id: Job identifier
            result: Analysis results
        """
        try:
            job_dir = self.get_job_dir(job_id)
            result_path = job_dir / "result.json"

            # Add metadata
            result['_metadata'] = {
                'job_id': job_id,
                'stored_at': datetime.utcnow().isoformat(),
                'storage_version': '1.0'
            }

            # Write result
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)

            logger.info(f"Stored result for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to store result for job {job_id}: {str(e)}")
            raise

    async def load_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Load analysis result.

        Args:
            job_id: Job identifier

        Returns:
            Analysis results or None if not found
        """
        try:
            job_dir = self.get_job_dir(job_id)
            result_path = job_dir / "result.json"

            if not result_path.exists():
                return None

            with open(result_path, 'r') as f:
                result = json.load(f)

            return result

        except Exception as e:
            logger.error(f"Failed to load result for job {job_id}: {str(e)}")
            return None

    async def delete_result(self, job_id: str):
        """
        Delete job results.

        Args:
            job_id: Job identifier
        """
        try:
            job_dir = self.get_job_dir(job_id)

            if job_dir.exists():
                import shutil
                shutil.rmtree(job_dir)
                logger.info(f"Deleted results for job {job_id}")

        except Exception as e:
            logger.error(f"Failed to delete results for job {job_id}: {str(e)}")
            raise

    async def list_jobs(self) -> list:
        """
        List all stored jobs.

        Returns:
            List of job IDs
        """
        try:
            job_dirs = [d.name for d in self.base_path.iterdir() if d.is_dir()]
            return sorted(job_dirs)
        except Exception as e:
            logger.error(f"Failed to list jobs: {str(e)}")
            return []

    async def cleanup_old_results(self, max_age_days: int = 7):
        """
        Clean up old results.

        Args:
            max_age_days: Maximum age in days
        """
        try:
            now = datetime.utcnow()
            removed_count = 0

            for job_dir in self.base_path.iterdir():
                if not job_dir.is_dir():
                    continue

                # Check age based on directory modification time
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                age_days = (now - mtime).days

                if age_days > max_age_days:
                    import shutil
                    shutil.rmtree(job_dir)
                    removed_count += 1

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old result directories")

        except Exception as e:
            logger.error(f"Failed to cleanup old results: {str(e)}")
