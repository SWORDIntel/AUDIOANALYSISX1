"""
API Data Models
===============

Pydantic models for API request/response validation.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    """Request model for audio analysis."""
    audio_data: Optional[str] = Field(None, description="Base64-encoded audio data")
    audio_url: Optional[HttpUrl] = Field(None, description="URL to audio file")
    asset_id: Optional[str] = Field(None, description="Custom asset identifier")
    save_visualizations: bool = Field(True, description="Generate visualization plots")
    webhook_url: Optional[HttpUrl] = Field(None, description="Webhook URL for async notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "https://example.com/audio.wav",
                "asset_id": "sample_001",
                "save_visualizations": True
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for audio analysis."""
    job_id: str = Field(..., description="Unique job identifier")
    status: AnalysisStatus = Field(..., description="Current job status")
    result: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "result": {
                    "ALTERATION_DETECTED": True,
                    "CONFIDENCE": "99% (Very High)",
                    "PRESENTED_AS": "Female",
                    "PROBABLE_SEX": "Male"
                },
                "created_at": "2025-11-05T10:30:00Z",
                "completed_at": "2025-11-05T10:30:05Z"
            }
        }


class StreamChunk(BaseModel):
    """Model for streaming audio chunks."""
    session_id: str = Field(..., description="Stream session identifier")
    chunk_index: int = Field(..., description="Sequential chunk number")
    audio_data: str = Field(..., description="Base64-encoded audio chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    sample_rate: int = Field(44100, description="Audio sample rate")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "stream_123",
                "chunk_index": 0,
                "audio_data": "UklGRiQAAABXQVZFZm10...",
                "is_final": False,
                "sample_rate": 44100
            }
        }


class StreamStatus(BaseModel):
    """Status update for streaming analysis."""
    session_id: str
    status: str
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage (0-1)")
    current_results: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class WebhookConfig(BaseModel):
    """Webhook configuration."""
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    events: List[str] = Field(
        default=["analysis.completed", "analysis.failed"],
        description="Events to trigger webhook"
    )
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    secret: Optional[str] = Field(None, description="Webhook signature secret")


class WebhookEvent(BaseModel):
    """Webhook event payload."""
    event: str = Field(..., description="Event name")
    job_id: str = Field(..., description="Associated job ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")
    signature: Optional[str] = Field(None, description="HMAC signature")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    uptime_seconds: float
    active_jobs: int
    total_processed: int


class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis."""
    audio_files: List[str] = Field(..., description="List of base64-encoded audio files or URLs")
    asset_ids: Optional[List[str]] = Field(None, description="Custom identifiers")
    save_visualizations: bool = Field(True, description="Generate visualizations")
    webhook_url: Optional[HttpUrl] = Field(None, description="Webhook for batch completion")


class ConfigUpdate(BaseModel):
    """Runtime configuration update."""
    max_workers: Optional[int] = Field(None, ge=1, le=32, description="Max parallel workers")
    cache_enabled: Optional[bool] = Field(None, description="Enable result caching")
    log_level: Optional[str] = Field(None, description="Logging level")
