# AUDIOANALYSISX1 v2.0 - API Features

## 🚀 New in Version 2.0

AUDIOANALYSISX1 v2.0 introduces a comprehensive **REST API and WebSocket interface** for integrating forensic audio analysis into your applications, along with an **extensible plugin system** for custom analyzers.

## 🌟 Key Features

### 1. REST API Server
- **FastAPI-powered** REST endpoints for audio analysis
- Async job processing with background workers
- File upload and URL-based analysis
- Batch processing for multiple files
- Interactive API documentation (Swagger/OpenAPI)

### 2. Real-time WebSocket Streaming
- Stream audio chunks for live analysis
- Progress updates during processing
- Low-latency results for real-time applications

### 3. Webhook Integration
- Event-driven notifications (analysis.completed, analysis.failed)
- HMAC signature verification for security
- Custom headers and secrets

### 4. Python Client SDK
- Easy-to-use client library
- Synchronous and asynchronous methods
- Streaming support with context managers
- Built-in retry logic and error handling

### 5. Plugin Architecture
- Extensible system for custom analyzers
- Processor plugins for audio preprocessing
- Visualizer plugins for custom plots
- Decorator-based registration
- Auto-discovery from plugin directories

### 6. Performance Optimizations
- Result caching for repeated analyses
- Parallel processing with configurable workers
- Batch processing with chunking
- Performance monitoring and metrics

### 7. Configuration Management
- JSON/YAML configuration files
- Environment variable support
- Runtime configuration updates via API
- Flexible settings for all components

### 8. Enhanced Storage
- File-based result storage
- Job history and tracking
- Automatic cleanup of old results
- Visualization retrieval

## 📋 Quick Start

### Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python run_api_server.py

# Or with custom settings
python run_api_server.py --port 9000 --workers 4 --max-workers 8
```

### Use the Python Client

```python
from audioanalysisx1.api import AudioAnalysisClient

# Initialize client
client = AudioAnalysisClient("http://localhost:8000")

# Analyze a file
job = client.analyze_file("audio.wav")

# Wait for result
result = client.wait_for_result(job['job_id'])

print(f"Manipulation detected: {result['ALTERATION_DETECTED']}")
print(f"Confidence: {result['CONFIDENCE']}")
```

### Stream Audio in Real-time

```python
import asyncio

async def stream_analysis():
    client = AudioAnalysisClient("http://localhost:8000")

    async with client.stream() as stream:
        for chunk in audio_chunks:
            await stream.send_chunk(chunk)

        result = await stream.get_result()
        print(result)

asyncio.run(stream_analysis())
```

### Create Custom Plugins

```python
from audioanalysisx1.plugins import AnalyzerPlugin, PluginMetadata, analyzer_plugin
import numpy as np

@analyzer_plugin("my_analyzer")
class MyAnalyzer(AnalyzerPlugin):
    """Custom audio analyzer."""

    def get_metadata(self):
        return PluginMetadata(
            name="my_analyzer",
            version="1.0.0",
            description="My custom analysis method",
            author="Your Name"
        )

    def analyze(self, audio_data, sample_rate, context=None):
        # Your analysis logic
        return {"custom_metric": calculate_metric(audio_data)}
```

## 🔌 API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `POST /analyze` - Analyze audio (base64 or URL)
- `POST /analyze/upload` - Upload and analyze file
- `GET /jobs/{job_id}` - Get job status and results
- `GET /jobs` - List jobs
- `DELETE /jobs/{job_id}` - Cancel job
- `POST /batch` - Batch analysis
- `GET /stats` - API statistics
- `PUT /config` - Update configuration

### Visualization Endpoints

- `GET /jobs/{job_id}/visualizations/{plot_name}` - Get plot image

### WebSocket

- `ws://host:port/stream` - Real-time streaming endpoint

## 📚 Documentation

- **API Guide**: [docs/API_GUIDE.md](docs/API_GUIDE.md)
- **Plugin Development**: [docs/PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)
- **Examples**: [examples/api_integration_example.py](examples/api_integration_example.py)
- **Interactive Docs**: http://localhost:8000/docs (when server is running)

## 🔧 Configuration

### Configuration File (config.json)

```json
{
  "analysis": {
    "f0_min": 75.0,
    "f0_max": 400.0,
    "use_gpu": false,
    "enable_caching": true
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "max_workers": 8,
    "storage_path": "./api_results"
  },
  "plugins": {
    "enabled": true,
    "plugin_dirs": ["./plugins"],
    "auto_discover": true
  }
}
```

### Environment Variables

```bash
export AUDIOANALYSIS_API_PORT=8000
export AUDIOANALYSIS_API_WORKERS=4
export AUDIOANALYSIS_ENABLE_CACHING=true
```

## 🌐 Integration Examples

### Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function analyzeAudio(filePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));

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
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

### cURL

```bash
# Upload and analyze
curl -X POST http://localhost:8000/analyze/upload \
  -F "file=@audio.wav" \
  -F "asset_id=test_001"

# Get job status
curl http://localhost:8000/jobs/{job_id}

# Health check
curl http://localhost:8000/health
```

## 🎨 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                     │
│  (Python SDK, Node.js, cURL, Custom Integrations)          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │ REST API   │  │ WebSocket  │  │ Webhook Manager    │   │
│  └────────────┘  └────────────┘  └────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Analysis Engine                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         5-Phase Detection Pipeline                     │  │
│  │  Phase 1: F0 → Phase 2: Formants → Phase 3: Artifacts│  │
│  │       → Phase 4: AI Detection → Phase 5: Report       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Plugin System                             │  │
│  │  Analyzer Plugins | Processor Plugins | Visualizers   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                Storage & Caching Layer                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │ Results DB │  │ Cache      │  │ Job Queue          │   │
│  └────────────┘  └────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Use Cases

1. **Security Applications**: Integrate into fraud detection systems
2. **Forensic Analysis**: Batch process evidence files
3. **Real-time Monitoring**: Stream audio from live sources
4. **Research Tools**: Add custom detection methods via plugins
5. **Automated Workflows**: Webhook-driven processing pipelines

## 🔒 Security Features

- Optional API key authentication
- HMAC webhook signatures
- Rate limiting
- Input validation
- Secure file handling

## 📈 Performance

- Parallel processing with configurable workers
- Result caching for repeated analyses
- Batch processing optimization
- Async job queue
- Average: ~1 second per 100ms of audio

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Development Mode

```bash
python run_api_server.py --reload --log-level debug
```

## 📦 Dependencies

All API dependencies are included in `requirements.txt`:
- FastAPI + Uvicorn for API server
- Pydantic for validation
- httpx for HTTP client
- websockets for streaming
- And all existing audio analysis libraries

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional plugin types
- More storage backends
- Authentication methods
- Performance optimizations

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- **GitHub**: https://github.com/SWORDIntel/AUDIOANALYSISX1
- **API Documentation**: http://localhost:8000/docs
- **Issues**: https://github.com/SWORDIntel/AUDIOANALYSISX1/issues
