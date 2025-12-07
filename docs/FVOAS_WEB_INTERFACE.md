# FVOAS Web Interface

**Classification: SECRET**  
**Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303**

## Overview

The FVOAS Web Interface provides a non-terminal based web UI for the Federal Voice Obfuscation and Analysis Suite. It can run using either:

1. **DSMilWebFrame** (recommended) - Full-featured framework integration
2. **Simple FastAPI** (fallback) - Basic web interface if framework unavailable

## Quick Start

### Using Simple Web Interface (No Framework Required)

```bash
# Install FastAPI and uvicorn
pip install fastapi uvicorn

# Launch web interface
python run_fvoas_web.py

# Custom port
python run_fvoas_web.py --port 8080

# Bind to all interfaces
python run_fvoas_web.py --host 0.0.0.0
```

Access at: `http://localhost:8080`

### Using DSMilWebFrame (Full Framework)

```bash
# Install DSMilWebFrame
pip install -e /path/to/DSMilWebFrame

# Launch with framework
python run_fvoas_web.py
```

## Features

### Simple Web Interface

- **System Status** - Real-time FVOAS status monitoring
- **Federal Compliance** - Compliance verification display
- **Preset Selection** - Click-to-apply anonymization presets
- **Telemetry** - Voice telemetry display
- **Auto-refresh** - Status updates every 5 seconds

### DSMilWebFrame Integration

- **Module-based Architecture** - Integrated as `fvoas_anonymization` module
- **Backend Abstraction** - Python backend for FVOAS operations
- **React Frontend** - Modern React UI (if framework React support enabled)
- **WebSocket Support** - Real-time updates via WebSocket
- **API Endpoints** - RESTful API for programmatic access

## API Endpoints

### Simple Interface

- `GET /` - Web UI
- `GET /api/status` - Get FVOAS status
- `GET /api/compliance` - Verify federal compliance
- `GET /api/presets` - List available presets
- `POST /api/set-preset/{preset_name}` - Apply preset
- `GET /api/telemetry` - Get latest telemetry

### Example API Usage

```python
import requests

# Get status
response = requests.get('http://localhost:8080/api/status')
status = response.json()
print(f"Running: {status['running']}")
print(f"Preset: {status['current_preset']}")

# Set preset
response = requests.post('http://localhost:8080/api/set-preset/anonymous_moderate')
result = response.json()
print(result['message'])

# Verify compliance
response = requests.get('http://localhost:8080/api/compliance')
compliance = response.json()
print(f"Federal Mandate: {compliance['compliance']['federal_mandate']}")
```

## Module Structure

### FVOASBackend

Python backend providing FVOAS operations:

- `initialize()` - Initialize FVOAS controller
- `get_status()` - Get current status
- `list_presets()` - List available presets
- `set_preset(preset_name)` - Apply anonymization preset
- `verify_compliance()` - Verify federal compliance
- `get_telemetry()` - Get latest telemetry
- `shutdown()` - Shutdown controller

### FVOASAnonymizationModule

DSMilWebFrame module wrapper:

- Extends `EngineModuleBase`
- Supports Web GUI framework
- Provides quick actions for common operations
- Integrates with framework's backend system

## Configuration

### Simple Interface

No configuration required - runs standalone.

### DSMilWebFrame

Configure in `config/backends.yaml`:

```yaml
backends:
  fvoas_backend:
    type: python
    config:
      module: "audioanalysisx1.fvoas.web_module"
      object: "FVOASBackend"

module_backends:
  fvoas_anonymization: fvoas_backend
```

## Security Considerations

- **Classification:** SECRET-level processing
- **Access Control:** Requires appropriate permissions
- **Device:** Device 9 (Audio) required
- **Layer:** Layer 3 (SECRET)
- **Clearance:** 0x03030303

## Compliance

The web interface maintains the same compliance status as the core FVOAS system:

- ✅ **CNSA 2.0 Compliant** (implementation)
- ✅ **NIST SP 800-63B Compliant** (implementation)
- ✅ **NIST SP 800-53 Compliant** (implementation)
- ✅ **Federal Mandate Compliant** (implementation)

**⚠️ Important:** The system is COMPLIANT but NOT AUDITED/CERTIFIED.

## Troubleshooting

### DSMilWebFrame Not Available

If DSMilWebFrame is not installed, the simple web interface will be used automatically.

### FastAPI Not Available

Install required dependencies:

```bash
pip install fastapi uvicorn
```

### FVOAS Controller Fails to Initialize

- Check kernel driver availability
- Verify device permissions
- Review system logs

## Integration Examples

### Standalone Usage

```python
from audioanalysisx1.fvoas.web_module import FVOASBackend

backend = FVOASBackend()
backend.initialize()

# Set preset
backend.set_preset('anonymous_moderate')

# Check compliance
compliance = backend.verify_compliance()
print(f"Federal Mandate: {compliance['compliance']['federal_mandate']}")

# Get status
status = backend.get_status()
print(f"Running: {status['running']}")
```

### With DSMilWebFrame

```python
from audioanalysisx1.fvoas.web_module import FVOASAnonymizationModule

module = FVOASAnonymizationModule()
module.perform_action('initialize')
status = module.get_status_summary()
```

## See Also

- [FVOAS Overview](FVOAS_OVERVIEW.md)
- [Federal Compliance](FEDERAL_COMPLIANCE.md)
- [Dynamic Anonymization](DYNAMIC_ANONYMIZATION.md)
- [DSMilWebFrame Documentation](../../../DSMilWebFrame/README.md)

---

**Classification: SECRET | Distribution: Authorized Personnel Only**
