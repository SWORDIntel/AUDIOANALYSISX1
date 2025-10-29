# Deployment Guide
## Voice Manipulation Detection Pipeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Performance Tuning](#performance-tuning)
5. [Monitoring & Logging](#monitoring--logging)
6. [Security Hardening](#security-hardening)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling Strategies](#scaling-strategies)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Environment Setup

### System Requirements

#### Minimum Specifications

- **CPU:** 2 cores (x86_64)
- **RAM:** 4 GB
- **Storage:** 10 GB available
- **OS:** Linux, macOS, or Windows
- **Python:** 3.10 or higher

#### Recommended Specifications

- **CPU:** 4+ cores (x86_64)
- **RAM:** 16 GB
- **Storage:** 50 GB SSD
- **OS:** Ubuntu 22.04 LTS or later
- **Python:** 3.11

### Installation

#### 1. Python Environment

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

#### 2. System Dependencies

**Ubuntu/Debian:**

```bash
sudo apt install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    python3-dev \
    build-essential
```

**macOS:**

```bash
brew install ffmpeg portaudio
```

**Windows:**

Download and install:
- [FFmpeg](https://ffmpeg.org/download.html)
- [Visual C++ Build Tools](https://visualstudio.microsoft.com/downloads/)

#### 3. Python Dependencies

```bash
cd /path/to/voice
pip install -r requirements.txt
```

#### 4. Verification

```bash
# Run test suite
python test_pipeline.py

# Expected: 4/4 manipulation detection tests pass
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Production Deployment

### Directory Structure

```
/opt/voice-detector/
├── app/
│   ├── phase1_baseline.py
│   ├── phase2_formants.py
│   ├── phase3_artifacts.py
│   ├── phase4_report.py
│   ├── pipeline.py
│   ├── verification.py
│   ├── visualizer.py
│   └── tui.py
│
├── data/
│   ├── input/          # Incoming audio files
│   ├── processing/     # Temporary processing directory
│   └── output/         # Analysis results
│
├── logs/
│   └── detector.log    # Application logs
│
├── venv/               # Virtual environment
├── requirements.txt
└── config.ini          # Configuration file
```

### Configuration File

**`config.ini`:**

```ini
[DEFAULT]
# Paths
input_dir = /opt/voice-detector/data/input
output_dir = /opt/voice-detector/data/output
temp_dir = /opt/voice-detector/data/processing
log_file = /opt/voice-detector/logs/detector.log

# Processing
max_workers = 4
enable_visualizations = false
max_audio_duration = 600  # 10 minutes

# Security
max_file_size = 104857600  # 100 MB
allowed_formats = wav,mp3,flac,ogg,m4a

# Logging
log_level = INFO
```

### Service Configuration

#### Systemd Service (Linux)

**`/etc/systemd/system/voice-detector.service`:**

```ini
[Unit]
Description=Voice Manipulation Detection Service
After=network.target

[Service]
Type=simple
User=voice-detector
Group=voice-detector
WorkingDirectory=/opt/voice-detector/app
Environment="PATH=/opt/voice-detector/venv/bin"
ExecStart=/opt/voice-detector/venv/bin/python pipeline.py --watch /opt/voice-detector/data/input

Restart=on-failure
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ReadWritePaths=/opt/voice-detector/data /opt/voice-detector/logs

# Resource limits
MemoryLimit=4G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-detector
sudo systemctl start voice-detector
sudo systemctl status voice-detector
```

### User Management

```bash
# Create dedicated user
sudo useradd -r -s /bin/false voice-detector

# Set permissions
sudo chown -R voice-detector:voice-detector /opt/voice-detector
sudo chmod 750 /opt/voice-detector/app
sudo chmod 770 /opt/voice-detector/data
sudo chmod 770 /opt/voice-detector/logs
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Docker Deployment

### Dockerfile

**`Dockerfile`:**

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY *.py ./

# Create non-root user
RUN useradd -m -u 1000 detector && \
    chown -R detector:detector /app

USER detector

# Volumes
VOLUME ["/data/input", "/data/output"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Entry point
ENTRYPOINT ["python", "pipeline.py"]
CMD ["--help"]
```

### Docker Compose

**`docker-compose.yml`:**

```yaml
version: '3.8'

services:
  voice-detector:
    build: .
    image: voice-detector:latest
    container_name: voice-detector

    volumes:
      - ./data/input:/data/input:ro
      - ./data/output:/data/output:rw
      - ./logs:/app/logs:rw

    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO

    restart: unless-stopped

    # Security
    security_opt:
      - no-new-privileges:true

    # Resource limits
    mem_limit: 4g
    cpus: 2.0

    # Network (offline mode)
    network_mode: none
```

### Build and Run

```bash
# Build image
docker build -t voice-detector:latest .

# Run container
docker-compose up -d

# View logs
docker-compose logs -f

# Analyze a file
docker run --rm \
    -v /path/to/audio:/data/input:ro \
    -v /path/to/results:/data/output:rw \
    voice-detector:latest \
    analyze /data/input/sample.wav -o /data/output/
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Performance Tuning

### Memory Optimization

#### Limit Audio Duration

```python
# In production, limit duration to prevent memory exhaustion
import librosa

MAX_DURATION = 300  # 5 minutes

y, sr = librosa.load(audio_path, duration=MAX_DURATION)
```

#### Disable Visualizations

```python
# For high-volume processing
report = detector.analyze(
    audio_path,
    save_visualizations=False  # Saves ~50% processing time
)
```

### CPU Optimization

#### Parallel Processing

```python
from multiprocessing import Pool
from pathlib import Path

def analyze_file(audio_path):
    detector = VoiceManipulationDetector()
    return detector.analyze(audio_path, save_visualizations=False)

if __name__ == '__main__':
    audio_files = list(Path('./input').glob('*.wav'))

    with Pool(processes=4) as pool:
        reports = pool.map(analyze_file, audio_files)
```

#### Reduce Hop Length

```python
# Trade accuracy for speed
analyzer = BaselineAnalyzer(hop_length=1024)  # Default: 512
```

### Disk I/O Optimization

```bash
# Use SSD for temp directory
export TMPDIR=/mnt/ssd/temp

# Or in Python
import os
os.environ['TMPDIR'] = '/mnt/ssd/temp'
```

### Benchmarks

| Configuration | Processing Time (3 min audio) | Memory Usage |
|---------------|------------------------------|--------------|
| Default (with viz) | ~35 seconds | ~800 MB |
| No viz | ~15 seconds | ~400 MB |
| hop_length=1024 | ~10 seconds | ~300 MB |
| Parallel (4 cores) | ~8 seconds/file | ~1.2 GB total |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Monitoring & Logging

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            '/opt/voice-detector/logs/detector.log',
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Metrics Collection

#### Track Analysis Metrics

```python
import time
from datetime import datetime

class MetricsCollector:
    def __init__(self):
        self.metrics = []

    def record_analysis(self, asset_id, duration, manipulation_detected, confidence):
        self.metrics.append({
            'timestamp': datetime.utcnow().isoformat(),
            'asset_id': asset_id,
            'duration': duration,
            'manipulation_detected': manipulation_detected,
            'confidence': confidence
        })

    def save_metrics(self, path='metrics.json'):
        with open(path, 'w') as f:
            json.dump(self.metrics, f, indent=2)

# Usage
metrics = MetricsCollector()

start = time.time()
report = detector.analyze('sample.wav')
duration = time.time() - start

metrics.record_analysis(
    asset_id=report['ASSET_ID'],
    duration=duration,
    manipulation_detected=report['ALTERATION_DETECTED'],
    confidence=report['CONFIDENCE']
)
```

### Health Checks

```bash
#!/bin/bash
# health_check.sh

# Check if service is running
systemctl is-active --quiet voice-detector
if [ $? -ne 0 ]; then
    echo "CRITICAL: Service not running"
    exit 2
fi

# Check disk space
usage=$(df -h /opt/voice-detector/data | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $usage -gt 90 ]; then
    echo "WARNING: Disk usage at ${usage}%"
    exit 1
fi

echo "OK: Service healthy"
exit 0
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Security Hardening

### Input Validation

```python
from pathlib import Path

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_FORMATS = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']

def validate_audio_file(audio_path):
    """Validate audio file before processing."""
    path = Path(audio_path)

    # Check existence
    if not path.exists():
        raise FileNotFoundError(f"File not found: {audio_path}")

    # Check size
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {path.stat().st_size} bytes")

    # Check format
    if path.suffix.lower() not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported format: {path.suffix}")

    return True
```

### Sandboxing

#### AppArmor Profile (Linux)

**`/etc/apparmor.d/voice-detector`:**

```
#include <tunables/global>

/opt/voice-detector/venv/bin/python {
    #include <abstractions/base>
    #include <abstractions/python>

    /opt/voice-detector/app/** r,
    /opt/voice-detector/data/** rw,
    /opt/voice-detector/logs/** rw,
    /opt/voice-detector/venv/** r,

    # Deny network access
    deny network,

    # Deny sensitive directories
    deny /etc/** r,
    deny /root/** rw,
    deny /home/** rw,
}
```

**Enable:**

```bash
sudo apparmor_parser -r /etc/apparmor.d/voice-detector
```

### File Permissions

```bash
# Restrict permissions
chmod 750 /opt/voice-detector/app
chmod 640 /opt/voice-detector/app/*.py
chmod 770 /opt/voice-detector/data
chmod 770 /opt/voice-detector/logs

# SELinux contexts (if applicable)
sudo chcon -R -t user_home_t /opt/voice-detector/data
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Backup & Recovery

### Backup Strategy

#### 1. Configuration Backup

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/voice-detector/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup configuration
cp /opt/voice-detector/config.ini $BACKUP_DIR/
cp /etc/systemd/system/voice-detector.service $BACKUP_DIR/

# Backup application
tar -czf $BACKUP_DIR/app.tar.gz /opt/voice-detector/app/

echo "Backup completed: $BACKUP_DIR"
```

#### 2. Results Backup

```bash
#!/bin/bash
# backup_results.sh

# Compress and archive old results
find /opt/voice-detector/data/output/ -type f -mtime +30 -name "*.json" \
    -exec tar -czf /backup/results_$(date +%Y%m).tar.gz {} +

# Upload to remote storage (optional)
# rsync -avz /backup/ remote:/backup/voice-detector/
```

### Disaster Recovery

#### Recovery Procedure

```bash
# 1. Stop service
sudo systemctl stop voice-detector

# 2. Restore configuration
sudo cp /backup/voice-detector/latest/config.ini /opt/voice-detector/

# 3. Restore application
sudo tar -xzf /backup/voice-detector/latest/app.tar.gz -C /

# 4. Restore permissions
sudo chown -R voice-detector:voice-detector /opt/voice-detector

# 5. Restart service
sudo systemctl start voice-detector
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Scaling Strategies

### Horizontal Scaling

#### Load Balancer Configuration

```
┌─────────────┐
│ Load        │
│ Balancer    │
└──────┬──────┘
       │
       ├────────┬────────┬────────┐
       │        │        │        │
   ┌───▼───┐┌───▼───┐┌───▼───┐┌───▼───┐
   │Worker ││Worker ││Worker ││Worker │
   │  #1   ││  #2   ││  #3   ││  #4   │
   └───────┘└───────┘└───────┘└───────┘
```

#### Queue-Based Processing

**Using RabbitMQ:**

```python
import pika
import json

def process_audio_task(ch, method, properties, body):
    """Process audio analysis task from queue."""
    task = json.loads(body)
    audio_path = task['audio_path']

    detector = VoiceManipulationDetector()
    report = detector.analyze(audio_path, save_visualizations=False)

    # Acknowledge task completion
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='audio_analysis', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='audio_analysis', on_message_callback=process_audio_task)

print('Waiting for tasks...')
channel.start_consuming()
```

### Vertical Scaling

#### GPU Acceleration (Future)

```python
# Placeholder for future GPU support
import torch

if torch.cuda.is_available():
    device = torch.device('cuda')
    # Accelerate STFT computations on GPU
else:
    device = torch.device('cpu')
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Production Checklist

### Pre-Deployment

- [ ] Test suite passes (100% manipulation detection)
- [ ] Resource requirements met
- [ ] System dependencies installed
- [ ] Virtual environment configured
- [ ] Configuration file created
- [ ] Log directory exists with correct permissions
- [ ] Dedicated user account created

### Security

- [ ] File permissions set correctly
- [ ] Input validation implemented
- [ ] Maximum file size enforced
- [ ] Network access disabled (if applicable)
- [ ] Sandboxing configured (AppArmor/SELinux)
- [ ] Sensitive directories protected

### Monitoring

- [ ] Logging configured
- [ ] Log rotation enabled
- [ ] Metrics collection implemented
- [ ] Health check script created
- [ ] Alerting configured (optional)

### Backup

- [ ] Backup script created
- [ ] Automated backup schedule configured
- [ ] Recovery procedure documented and tested
- [ ] Remote backup configured (if required)

### Documentation

- [ ] Configuration documented
- [ ] Deployment procedure documented
- [ ] Recovery procedure documented
- [ ] Team trained on operations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Support & Maintenance

### Regular Maintenance

```bash
# Weekly: Check logs for errors
tail -n 1000 /opt/voice-detector/logs/detector.log | grep ERROR

# Monthly: Rotate logs manually if needed
logrotate -f /etc/logrotate.d/voice-detector

# Quarterly: Update dependencies
source /opt/voice-detector/venv/bin/activate
pip list --outdated
pip install --upgrade librosa numpy scipy
```

### Troubleshooting

See [USAGE.md](USAGE.md#troubleshooting) for common issues.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
