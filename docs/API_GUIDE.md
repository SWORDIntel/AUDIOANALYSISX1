# AUDIOANALYSISX1 API Guide

## Overview

The AUDIOANALYSISX1 API provides REST and WebSocket interfaces for integrating forensic audio manipulation detection into your applications.

## Features

- **REST API**: HTTP endpoints for file upload and analysis
- **WebSocket**: Real-time streaming audio analysis
- **Async Processing**: Background job queue with webhook notifications
- **Batch Processing**: Analyze multiple files simultaneously
- **Plugin System**: Extensible architecture for custom analyzers
- **Caching**: Result caching for improved performance
- **Configuration**: Flexible configuration via files or environment variables

## Quick Start

### 1. Start the API Server

```bash
# Basic usage
python run_api_server.py

# Custom port and workers
python run_api_server.py --port 9000 --workers 4 --max-workers 8

# Development mode with auto-reload
python run_api_server.py --reload --log-level debug
```

### 2. Use the Python Client

```python
from audioanalysisx1.api import AudioAnalysisClient

# Initialize client
client = AudioAnalysisClient("http://localhost:8000")

# Analyze a file
job = client.analyze_file("audio.wav")
print(f"Job ID: {job['job_id']}")

# Wait for result
result = client.wait_for_result(job['job_id'])
print(f"Alteration detected: {result['ALTERATION_DETECTED']}")
print(f"Confidence: {result['CONFIDENCE']}")
```

## REST API Endpoints

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime_seconds": 3600.5,
  "active_jobs": 2,
  "total_processed": 150
}
```

### Analyze Audio (Base64)

```bash
POST /analyze
```

**Request:**
```json
{
  "audio_data": "UklGRiQAAABXQVZFZm10...",
  "asset_id": "sample_001",
  "save_visualizations": true,
  "webhook_url": "https://example.com/webhook"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2025-11-05T10:30:00Z"
}
```

### Analyze Audio (URL)

```bash
POST /analyze
```

**Request:**
```json
{
  "audio_url": "https://example.com/audio.wav",
  "asset_id": "sample_002",
  "save_visualizations": true
}
```

### Upload and Analyze

```bash
POST /analyze/upload
Content-Type: multipart/form-data

file: <audio_file>
asset_id: sample_003
save_visualizations: true
```

### Get Job Status

```bash
GET /jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "ALTERATION_DETECTED": true,
    "CONFIDENCE": "99% (Very High)",
    "PRESENTED_AS": "Female",
    "PROBABLE_SEX": "Male",
    "DECEPTION_BASELINE_F0": "221.5 Hz",
    "PHYSICAL_BASELINE_FORMANTS": "F1: 498 Hz, F2: 1510 Hz, F3: 2645 Hz"
  },
  "created_at": "2025-11-05T10:30:00Z",
  "completed_at": "2025-11-05T10:30:05Z"
}
```

### List Jobs

```bash
GET /jobs?status=completed&limit=10&offset=0
```

### Cancel Job

```bash
DELETE /jobs/{job_id}
```

### Get Visualization

```bash
GET /jobs/{job_id}/visualizations/{plot_name}
```

Plot names: `overview`, `spectrogram`, `phase_coherence`, `pitch_formant`

### Batch Analysis

```bash
POST /batch
```

**Request:**
```json
{
  "audio_files": [
    "base64_audio_1...",
    "https://example.com/audio2.wav"
  ],
  "asset_ids": ["sample_001", "sample_002"],
  "save_visualizations": true
}
```

**Response:**
```json
{
  "batch_id": "batch_123",
  "job_ids": [
    "job_001",
    "job_002"
  ],
  "total_jobs": 2
}
```

### Register Webhook

```bash
POST /webhooks
```

**Request:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["analysis.completed", "analysis.failed"],
  "secret": "webhook_secret_key"
}
```

### Get Statistics

```bash
GET /stats
```

**Response:**
```json
{
  "total_processed": 1500,
  "total_failed": 12,
  "total_streaming_sessions": 50,
  "active_jobs": 3,
  "uptime_seconds": 86400
}
```

### Update Configuration

```bash
PUT /config
```

**Request:**
```json
{
  "max_workers": 8,
  "cache_enabled": true,
  "log_level": "debug"
}
```

## WebSocket Streaming

### Connect and Stream Audio

```python
import asyncio
from audioanalysisx1.api import AudioAnalysisClient

async def stream_analysis():
    client = AudioAnalysisClient("http://localhost:8000")

    async with client.stream() as stream:
        # Send audio chunks
        for chunk in audio_chunks:
            response = await stream.send_chunk(chunk, is_final=False)
            print(f"Progress: {response.get('progress', 0):.1%}")

        # Send final chunk
        await stream.send_chunk(last_chunk, is_final=True)

        # Get result
        result = await stream.get_result()
        print(f"Analysis complete: {result}")

asyncio.run(stream_analysis())
```

### WebSocket Protocol

**1. Connect**
```
ws://localhost:8000/stream
```

**2. Receive Session Start**
```json
{
  "type": "session_start",
  "session_id": "stream_abc123",
  "message": "Streaming session started"
}
```

**3. Send Audio Chunks**
```json
{
  "type": "audio_chunk",
  "session_id": "stream_abc123",
  "chunk_index": 0,
  "audio_data": "base64_encoded_audio...",
  "is_final": false,
  "sample_rate": 44100
}
```

**4. Receive Progress Updates**
```json
{
  "type": "progress",
  "session_id": "stream_abc123",
  "progress": 0.45,
  "chunks_received": 10
}
```

**5. Receive Final Result**
```json
{
  "type": "analysis_complete",
  "session_id": "stream_abc123",
  "result": {
    "ALTERATION_DETECTED": true,
    "CONFIDENCE": "High"
  }
}
```

## Webhooks

When you provide a `webhook_url`, the API will send POST requests on events:

**Event: analysis.completed**
```json
{
  "event": "analysis.completed",
  "job_id": "job_123",
  "timestamp": "2025-11-05T10:30:05Z",
  "data": {
    "ALTERATION_DETECTED": true,
    "CONFIDENCE": "99% (Very High)"
  },
  "signature": "hmac_signature_if_secret_provided"
}
```

**Event: analysis.failed**
```json
{
  "event": "analysis.failed",
  "job_id": "job_123",
  "timestamp": "2025-11-05T10:30:05Z",
  "data": {
    "error": "Failed to process audio file"
  }
}
```

## Python Client Examples

### Basic Analysis

```python
from audioanalysisx1.api import AudioAnalysisClient

client = AudioAnalysisClient("http://localhost:8000")

# Analyze file
job = client.analyze_file("audio.wav", asset_id="test_001")

# Wait for completion
result = client.wait_for_result(job['job_id'], timeout=300)

# Check result
if result['ALTERATION_DETECTED']:
    print(f"Manipulation detected with {result['CONFIDENCE']} confidence")
    print(f"Presented as: {result['PRESENTED_AS']}")
    print(f"Probable sex: {result['PROBABLE_SEX']}")
```

### Async Analysis with Webhook

```python
client = AudioAnalysisClient("http://localhost:8000")

# Submit job with webhook
job = client.analyze_file(
    "audio.wav",
    webhook_url="https://myapp.com/webhook"
)

print(f"Job submitted: {job['job_id']}")
# Your webhook will be called when complete
```

### Batch Processing

```python
client = AudioAnalysisClient("http://localhost:8000")

# Analyze multiple files
files = ["audio1.wav", "audio2.wav", "audio3.wav"]
batch = client.batch_analyze(
    files,
    asset_ids=["sample_001", "sample_002", "sample_003"]
)

print(f"Batch ID: {batch['batch_id']}")
print(f"Job IDs: {batch['job_ids']}")

# Wait for all jobs
for job_id in batch['job_ids']:
    result = client.wait_for_result(job_id)
    print(f"Job {job_id}: {result['ALTERATION_DETECTED']}")
```

### Get Visualization

```python
client = AudioAnalysisClient("http://localhost:8000")

# Get job
job = client.analyze_file("audio.wav")
result = client.wait_for_result(job['job_id'])

# Download visualization
client.get_visualization(
    job['job_id'],
    'overview',
    save_path='overview.png'
)
```

### Upload File

```python
client = AudioAnalysisClient("http://localhost:8000")

# Upload and analyze
job = client.upload_file("audio.wav", asset_id="upload_001")
result = client.wait_for_result(job['job_id'])
```

## Configuration

### Configuration File (config.json)

```json
{
  "analysis": {
    "f0_min": 75.0,
    "f0_max": 400.0,
    "use_gpu": false,
    "enable_caching": true,
    "cache_dir": "./.cache"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "max_workers": 8,
    "storage_path": "./api_results",
    "max_file_size_mb": 100,
    "rate_limit_enabled": true
  },
  "plugins": {
    "enabled": true,
    "plugin_dirs": ["./plugins"],
    "auto_discover": true
  },
  "log_level": "INFO"
}
```

### Environment Variables

```bash
# Analysis
export AUDIOANALYSIS_F0_MIN=75.0
export AUDIOANALYSIS_USE_GPU=false
export AUDIOANALYSIS_ENABLE_CACHING=true

# API
export AUDIOANALYSIS_API_HOST=0.0.0.0
export AUDIOANALYSIS_API_PORT=8000
export AUDIOANALYSIS_API_WORKERS=4
export AUDIOANALYSIS_API_MAX_WORKERS=8

# Plugins
export AUDIOANALYSIS_PLUGINS_ENABLED=true

# Logging
export AUDIOANALYSIS_LOG_LEVEL=INFO
```

## Integration Examples

### Flask Application

```python
from flask import Flask, request, jsonify
from audioanalysisx1.api import AudioAnalysisClient

app = Flask(__name__)
client = AudioAnalysisClient("http://localhost:8000")

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['audio']
    file.save('temp.wav')

    job = client.analyze_file('temp.wav')
    result = client.wait_for_result(job['job_id'])

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### Node.js Application

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function analyzeAudio(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('asset_id', 'node_test');

  // Submit job
  const response = await axios.post(
    'http://localhost:8000/analyze/upload',
    form,
    { headers: form.getHeaders() }
  );

  const jobId = response.data.job_id;

  // Poll for result
  while (true) {
    const job = await axios.get(`http://localhost:8000/jobs/${jobId}`);

    if (job.data.status === 'completed') {
      return job.data.result;
    } else if (job.data.status === 'failed') {
      throw new Error(job.data.error);
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

analyzeAudio('audio.wav').then(result => {
  console.log('Analysis:', result);
});
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Upload and analyze
curl -X POST http://localhost:8000/analyze/upload \
  -F "file=@audio.wav" \
  -F "asset_id=curl_test"

# Get job status
curl http://localhost:8000/jobs/550e8400-e29b-41d4-a716-446655440000

# Get statistics
curl http://localhost:8000/stats
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid request
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

The API supports optional rate limiting. Configure in `config.json`:

```json
{
  "api": {
    "rate_limit_enabled": true,
    "rate_limit_requests_per_minute": 60
  }
}
```

## Performance Tips

1. **Enable Caching**: Set `enable_caching: true` to cache repeated analyses
2. **Adjust Workers**: Increase `max_workers` for more concurrent jobs
3. **Use Batch API**: Batch processing is more efficient than individual requests
4. **Optimize Threads**: Set `OMP_NUM_THREADS` environment variable
5. **Use WebSocket**: Streaming is more efficient for real-time analysis

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.
