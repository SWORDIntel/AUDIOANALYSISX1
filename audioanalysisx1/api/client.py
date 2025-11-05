"""
API Client SDK
==============

Python client for interacting with AUDIOANALYSISX1 API.
"""

import base64
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
import json

import httpx
import websockets


class AudioAnalysisClient:
    """
    Client for AUDIOANALYSISX1 API.

    Example usage:
        client = AudioAnalysisClient("http://localhost:8000")

        # Analyze a file
        job = client.analyze_file("audio.wav")
        print(f"Job ID: {job['job_id']}")

        # Wait for completion
        result = client.wait_for_result(job['job_id'])
        print(f"Alteration detected: {result['ALTERATION_DETECTED']}")

        # Stream audio
        async with client.stream() as stream:
            for chunk in audio_chunks:
                await stream.send_chunk(chunk)
            result = await stream.get_result()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL of API server
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        self.client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout
        )
        self.async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout
        )

    # ========================================================================
    # Synchronous Methods
    # ========================================================================

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = self.client.get('/health')
        response.raise_for_status()
        return response.json()

    def analyze_file(
        self,
        file_path: str,
        asset_id: Optional[str] = None,
        save_visualizations: bool = True,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an audio file.

        Args:
            file_path: Path to audio file
            asset_id: Optional asset identifier
            save_visualizations: Generate visualizations
            webhook_url: Optional webhook for completion notification

        Returns:
            Job information including job_id
        """
        # Read and encode file
        audio_data = Path(file_path).read_bytes()
        encoded = base64.b64encode(audio_data).decode('utf-8')

        # Submit analysis
        response = self.client.post('/analyze', json={
            'audio_data': encoded,
            'asset_id': asset_id,
            'save_visualizations': save_visualizations,
            'webhook_url': webhook_url
        })
        response.raise_for_status()
        return response.json()

    def analyze_url(
        self,
        audio_url: str,
        asset_id: Optional[str] = None,
        save_visualizations: bool = True,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze audio from URL.

        Args:
            audio_url: URL to audio file
            asset_id: Optional asset identifier
            save_visualizations: Generate visualizations
            webhook_url: Optional webhook for completion notification

        Returns:
            Job information including job_id
        """
        response = self.client.post('/analyze', json={
            'audio_url': audio_url,
            'asset_id': asset_id,
            'save_visualizations': save_visualizations,
            'webhook_url': webhook_url
        })
        response.raise_for_status()
        return response.json()

    def upload_file(
        self,
        file_path: str,
        asset_id: Optional[str] = None,
        save_visualizations: bool = True
    ) -> Dict[str, Any]:
        """
        Upload and analyze audio file.

        Args:
            file_path: Path to audio file
            asset_id: Optional asset identifier
            save_visualizations: Generate visualizations

        Returns:
            Job information
        """
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            data = {
                'asset_id': asset_id,
                'save_visualizations': save_visualizations
            }
            response = self.client.post('/analyze/upload', files=files, data=data)
            response.raise_for_status()
            return response.json()

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status and results.

        Args:
            job_id: Job identifier

        Returns:
            Job information
        """
        response = self.client.get(f'/jobs/{job_id}')
        response.raise_for_status()
        return response.json()

    def wait_for_result(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """
        Wait for job completion and return results.

        Args:
            job_id: Job identifier
            poll_interval: Polling interval in seconds
            timeout: Maximum wait time in seconds

        Returns:
            Analysis results

        Raises:
            TimeoutError: If job doesn't complete within timeout
            RuntimeError: If job fails
        """
        start_time = time.time()

        while True:
            job = self.get_job(job_id)

            if job['status'] == 'completed':
                return job['result']
            elif job['status'] == 'failed':
                raise RuntimeError(f"Job failed: {job.get('error', 'Unknown error')}")

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

            time.sleep(poll_interval)

    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List jobs.

        Args:
            status: Filter by status
            limit: Maximum results
            offset: Result offset

        Returns:
            List of jobs
        """
        params = {'limit': limit, 'offset': offset}
        if status:
            params['status'] = status

        response = self.client.get('/jobs', params=params)
        response.raise_for_status()
        return response.json()['jobs']

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a job.

        Args:
            job_id: Job identifier

        Returns:
            Cancellation confirmation
        """
        response = self.client.delete(f'/jobs/{job_id}')
        response.raise_for_status()
        return response.json()

    def get_visualization(self, job_id: str, plot_name: str, save_path: Optional[str] = None) -> bytes:
        """
        Get visualization plot.

        Args:
            job_id: Job identifier
            plot_name: Plot name (e.g., 'overview', 'spectrogram')
            save_path: Optional path to save image

        Returns:
            Image bytes
        """
        response = self.client.get(f'/jobs/{job_id}/visualizations/{plot_name}')
        response.raise_for_status()

        image_data = response.content
        if save_path:
            Path(save_path).write_bytes(image_data)

        return image_data

    def batch_analyze(
        self,
        file_paths: List[str],
        asset_ids: Optional[List[str]] = None,
        save_visualizations: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze multiple files in batch.

        Args:
            file_paths: List of file paths
            asset_ids: Optional list of asset identifiers
            save_visualizations: Generate visualizations

        Returns:
            Batch information including job IDs
        """
        audio_files = []
        for path in file_paths:
            audio_data = Path(path).read_bytes()
            encoded = base64.b64encode(audio_data).decode('utf-8')
            audio_files.append(encoded)

        response = self.client.post('/batch', json={
            'audio_files': audio_files,
            'asset_ids': asset_ids,
            'save_visualizations': save_visualizations
        })
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get API statistics."""
        response = self.client.get('/stats')
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # Async Methods
    # ========================================================================

    async def analyze_file_async(
        self,
        file_path: str,
        asset_id: Optional[str] = None,
        save_visualizations: bool = True,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Async version of analyze_file."""
        audio_data = Path(file_path).read_bytes()
        encoded = base64.b64encode(audio_data).decode('utf-8')

        response = await self.async_client.post('/analyze', json={
            'audio_data': encoded,
            'asset_id': asset_id,
            'save_visualizations': save_visualizations,
            'webhook_url': webhook_url
        })
        response.raise_for_status()
        return response.json()

    async def wait_for_result_async(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """Async version of wait_for_result."""
        start_time = time.time()

        while True:
            response = await self.async_client.get(f'/jobs/{job_id}')
            response.raise_for_status()
            job = response.json()

            if job['status'] == 'completed':
                return job['result']
            elif job['status'] == 'failed':
                raise RuntimeError(f"Job failed: {job.get('error', 'Unknown error')}")

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

            await asyncio.sleep(poll_interval)

    def stream(self) -> 'StreamingSession':
        """
        Create streaming session.

        Returns:
            StreamingSession context manager
        """
        return StreamingSession(self.base_url.replace('http', 'ws'))

    def close(self):
        """Close client connections."""
        self.client.close()

    async def aclose(self):
        """Async close client connections."""
        await self.async_client.aclose()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()


class StreamingSession:
    """WebSocket streaming session."""

    def __init__(self, ws_url: str):
        """
        Initialize streaming session.

        Args:
            ws_url: WebSocket URL
        """
        self.ws_url = f"{ws_url}/stream"
        self.websocket = None
        self.session_id = None
        self.chunk_index = 0

    async def __aenter__(self):
        """Connect to WebSocket."""
        self.websocket = await websockets.connect(self.ws_url)

        # Receive session start message
        message = await self.websocket.recv()
        data = json.loads(message)
        self.session_id = data['session_id']

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()

    async def send_chunk(
        self,
        audio_data: bytes,
        is_final: bool = False,
        sample_rate: int = 44100
    ):
        """
        Send audio chunk.

        Args:
            audio_data: Audio data bytes
            is_final: Whether this is the final chunk
            sample_rate: Audio sample rate
        """
        encoded = base64.b64encode(audio_data).decode('utf-8')

        await self.websocket.send(json.dumps({
            'type': 'audio_chunk',
            'session_id': self.session_id,
            'chunk_index': self.chunk_index,
            'audio_data': encoded,
            'is_final': is_final,
            'sample_rate': sample_rate
        }))

        self.chunk_index += 1

        # Receive progress update
        message = await self.websocket.recv()
        return json.loads(message)

    async def get_result(self) -> Dict[str, Any]:
        """
        Get final analysis result.

        Returns:
            Analysis results
        """
        while True:
            message = await self.websocket.recv()
            data = json.loads(message)

            if data['type'] == 'analysis_complete':
                return data['result']
            elif data['type'] == 'error':
                raise RuntimeError(f"Stream analysis failed: {data.get('error')}")

    async def cancel(self):
        """Cancel streaming session."""
        await self.websocket.send(json.dumps({
            'type': 'cancel',
            'session_id': self.session_id
        }))
