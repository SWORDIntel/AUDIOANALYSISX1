"""
FastAPI Server
==============

REST API and WebSocket server for audio analysis.
"""

import asyncio
import base64
import io
import time
import uuid
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import tempfile
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, File, UploadFile, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..pipeline import VoiceManipulationDetector
from .models import (
    AnalysisRequest, AnalysisResponse, AnalysisStatus,
    StreamChunk, StreamStatus, WebhookConfig, WebhookEvent,
    HealthResponse, BatchAnalysisRequest, ConfigUpdate
)
from .stream_handler import StreamingAudioHandler
from .job_queue import JobQueue
from .webhook_manager import WebhookManager
from .storage import ResultStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AUDIOANALYSISX1 API",
    description="Forensic Audio Manipulation Detection API with Real-time Analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class APIServer:
    """Main API server class."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize API server."""
        self.config = config or {}
        self.detector = VoiceManipulationDetector()
        self.job_queue = JobQueue(max_workers=self.config.get('max_workers', 4))
        self.webhook_manager = WebhookManager()
        self.storage = ResultStorage(self.config.get('storage_path', './api_results'))
        self.stream_handlers: Dict[str, StreamingAudioHandler] = {}
        self.start_time = time.time()
        self.stats = {
            'total_processed': 0,
            'total_failed': 0,
            'total_streaming_sessions': 0
        }

    async def analyze_audio(
        self,
        job_id: str,
        audio_path: str,
        asset_id: Optional[str] = None,
        save_visualizations: bool = True,
        webhook_url: Optional[str] = None
    ):
        """Perform audio analysis asynchronously."""
        try:
            logger.info(f"Starting analysis for job {job_id}")

            # Update job status
            await self.job_queue.update_job(job_id, AnalysisStatus.PROCESSING)

            # Perform analysis
            output_dir = self.storage.get_job_dir(job_id)
            result = self.detector.analyze(
                audio_path=audio_path,
                output_dir=str(output_dir),
                save_visualizations=save_visualizations,
                asset_id=asset_id
            )

            # Store result
            await self.storage.store_result(job_id, result)

            # Update job
            await self.job_queue.complete_job(job_id, result)

            # Update stats
            self.stats['total_processed'] += 1

            # Trigger webhook if configured
            if webhook_url:
                await self.webhook_manager.send_webhook(
                    url=webhook_url,
                    event='analysis.completed',
                    job_id=job_id,
                    data=result
                )

            logger.info(f"Completed analysis for job {job_id}")

        except Exception as e:
            logger.error(f"Analysis failed for job {job_id}: {str(e)}")
            await self.job_queue.fail_job(job_id, str(e))
            self.stats['total_failed'] += 1

            if webhook_url:
                await self.webhook_manager.send_webhook(
                    url=webhook_url,
                    event='analysis.failed',
                    job_id=job_id,
                    data={'error': str(e)}
                )

    def get_active_jobs_count(self) -> int:
        """Get count of active jobs."""
        return self.job_queue.get_active_count()

    def cleanup_session(self, session_id: str):
        """Cleanup streaming session."""
        if session_id in self.stream_handlers:
            del self.stream_handlers[session_id]


# Global server instance
server = APIServer()


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint."""
    return {
        "message": "AUDIOANALYSISX1 API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - server.start_time
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        uptime_seconds=uptime,
        active_jobs=server.get_active_jobs_count(),
        total_processed=server.stats['total_processed']
    )


@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_audio(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze audio file for manipulation detection.

    Supports:
    - Base64-encoded audio data
    - Audio file URL
    - Async processing with webhooks
    """
    job_id = str(uuid.uuid4())

    # Create temporary file for audio
    temp_dir = Path(tempfile.gettempdir()) / "audioanalysisx1"
    temp_dir.mkdir(exist_ok=True)

    audio_path = None

    try:
        if request.audio_data:
            # Decode base64 audio
            audio_bytes = base64.b64decode(request.audio_data)
            audio_path = temp_dir / f"{job_id}.wav"
            audio_path.write_bytes(audio_bytes)

        elif request.audio_url:
            # Download audio from URL
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(str(request.audio_url))
                response.raise_for_status()
                audio_path = temp_dir / f"{job_id}.wav"
                audio_path.write_bytes(response.content)
        else:
            raise HTTPException(status_code=400, detail="Must provide either audio_data or audio_url")

        # Create job
        job = await server.job_queue.create_job(
            job_id=job_id,
            audio_path=str(audio_path),
            asset_id=request.asset_id
        )

        # Start analysis in background
        background_tasks.add_task(
            server.analyze_audio,
            job_id=job_id,
            audio_path=str(audio_path),
            asset_id=request.asset_id,
            save_visualizations=request.save_visualizations,
            webhook_url=str(request.webhook_url) if request.webhook_url else None
        )

        return AnalysisResponse(
            job_id=job_id,
            status=AnalysisStatus.PENDING,
            created_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Failed to create analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/upload", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_upload(
    file: UploadFile = File(...),
    asset_id: Optional[str] = None,
    save_visualizations: bool = True,
    webhook_url: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Analyze uploaded audio file.
    """
    job_id = str(uuid.uuid4())

    try:
        # Save uploaded file
        temp_dir = Path(tempfile.gettempdir()) / "audioanalysisx1"
        temp_dir.mkdir(exist_ok=True)
        audio_path = temp_dir / f"{job_id}_{file.filename}"

        content = await file.read()
        audio_path.write_bytes(content)

        # Create job
        job = await server.job_queue.create_job(
            job_id=job_id,
            audio_path=str(audio_path),
            asset_id=asset_id
        )

        # Start analysis in background
        background_tasks.add_task(
            server.analyze_audio,
            job_id=job_id,
            audio_path=str(audio_path),
            asset_id=asset_id,
            save_visualizations=save_visualizations,
            webhook_url=webhook_url
        )

        return AnalysisResponse(
            job_id=job_id,
            status=AnalysisStatus.PENDING,
            created_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Failed to process upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}", response_model=AnalysisResponse, tags=["Jobs"])
async def get_job_status(job_id: str):
    """Get analysis job status and results."""
    job = await server.job_queue.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.get("/jobs", tags=["Jobs"])
async def list_jobs(
    status: Optional[AnalysisStatus] = None,
    limit: int = 100,
    offset: int = 0
):
    """List analysis jobs."""
    jobs = await server.job_queue.list_jobs(status=status, limit=limit, offset=offset)
    return {"jobs": jobs, "total": len(jobs)}


@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def cancel_job(job_id: str):
    """Cancel a pending or processing job."""
    success = await server.job_queue.cancel_job(job_id)

    if not success:
        raise HTTPException(status_code=404, detail="Job not found or already completed")

    return {"message": "Job cancelled successfully"}


@app.get("/jobs/{job_id}/visualizations/{plot_name}", tags=["Jobs"])
async def get_visualization(job_id: str, plot_name: str):
    """Get visualization plot for a job."""
    job_dir = server.storage.get_job_dir(job_id)
    plot_path = job_dir / f"{plot_name}.png"

    if not plot_path.exists():
        raise HTTPException(status_code=404, detail="Visualization not found")

    return FileResponse(
        plot_path,
        media_type="image/png",
        filename=f"{job_id}_{plot_name}.png"
    )


@app.post("/batch", tags=["Analysis"])
async def batch_analyze(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze multiple audio files in batch.
    """
    batch_id = str(uuid.uuid4())
    job_ids = []

    for idx, audio_file in enumerate(request.audio_files):
        asset_id = request.asset_ids[idx] if request.asset_ids and idx < len(request.asset_ids) else None

        # Create individual analysis request
        analysis_req = AnalysisRequest(
            audio_data=audio_file if not audio_file.startswith('http') else None,
            audio_url=audio_file if audio_file.startswith('http') else None,
            asset_id=asset_id,
            save_visualizations=request.save_visualizations
        )

        # Submit job
        response = await analyze_audio(analysis_req, background_tasks)
        job_ids.append(response.job_id)

    return {
        "batch_id": batch_id,
        "job_ids": job_ids,
        "total_jobs": len(job_ids)
    }


@app.post("/webhooks", tags=["Webhooks"])
async def register_webhook(webhook: WebhookConfig):
    """Register a webhook for event notifications."""
    webhook_id = await server.webhook_manager.register_webhook(webhook)
    return {"webhook_id": webhook_id, "message": "Webhook registered successfully"}


@app.get("/stats", tags=["General"])
async def get_stats():
    """Get API statistics."""
    return {
        "total_processed": server.stats['total_processed'],
        "total_failed": server.stats['total_failed'],
        "total_streaming_sessions": server.stats['total_streaming_sessions'],
        "active_jobs": server.get_active_jobs_count(),
        "uptime_seconds": time.time() - server.start_time
    }


@app.put("/config", tags=["Configuration"])
async def update_config(config: ConfigUpdate):
    """Update runtime configuration."""
    if config.max_workers is not None:
        server.config['max_workers'] = config.max_workers
        server.job_queue.update_max_workers(config.max_workers)

    if config.cache_enabled is not None:
        server.config['cache_enabled'] = config.cache_enabled

    if config.log_level is not None:
        logging.getLogger().setLevel(config.log_level.upper())

    return {"message": "Configuration updated", "config": server.config}


# ============================================================================
# WebSocket Endpoint for Streaming
# ============================================================================

@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming audio analysis.

    Protocol:
    1. Client connects and sends session metadata
    2. Client streams audio chunks
    3. Server sends progress updates
    4. Server sends final analysis when stream ends
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    handler = None

    try:
        logger.info(f"WebSocket connection established: {session_id}")
        server.stats['total_streaming_sessions'] += 1

        # Initialize streaming handler
        handler = StreamingAudioHandler(
            session_id=session_id,
            detector=server.detector
        )
        server.stream_handlers[session_id] = handler

        # Send session ID
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id,
            "message": "Streaming session started"
        })

        # Process incoming chunks
        while True:
            try:
                data = await websocket.receive_json()

                if data.get('type') == 'audio_chunk':
                    chunk = StreamChunk(**data)

                    # Add chunk to handler
                    await handler.add_chunk(chunk)

                    # Send progress update
                    progress = await handler.get_progress()
                    await websocket.send_json({
                        "type": "progress",
                        "session_id": session_id,
                        "progress": progress,
                        "chunks_received": chunk.chunk_index + 1
                    })

                    # If final chunk, analyze
                    if chunk.is_final:
                        logger.info(f"Received final chunk for session {session_id}")
                        result = await handler.finalize_and_analyze()

                        await websocket.send_json({
                            "type": "analysis_complete",
                            "session_id": session_id,
                            "result": result
                        })
                        break

                elif data.get('type') == 'cancel':
                    logger.info(f"Session cancelled: {session_id}")
                    await websocket.send_json({
                        "type": "cancelled",
                        "session_id": session_id
                    })
                    break

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {session_id}")
                break

    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "session_id": session_id,
                "error": str(e)
            })
        except:
            pass
    finally:
        # Cleanup
        if handler:
            await handler.cleanup()
        server.cleanup_session(session_id)
        try:
            await websocket.close()
        except:
            pass


# ============================================================================
# Server Runner
# ============================================================================

def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info"
):
    """Run the API server."""
    uvicorn.run(
        "audioanalysisx1.api.server:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level
    )


if __name__ == "__main__":
    run_server()
