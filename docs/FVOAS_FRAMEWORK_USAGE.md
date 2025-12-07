# FVOAS Framework Usage

**Classification: SECRET**  
**Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303**

## Using DSMilWebFrame Properly

FVOAS is integrated with DSMilWebFrame using the framework's proper scaffolding and entry points, not custom launchers.

## Proper Usage (Framework Commands)

### TUI Interface

```bash
# Using framework's dsmil command
dsmil --module fvoas_anonymization
```

### Qt Desktop GUI

```bash
# Using framework's Qt launcher
python -m dsmil_framework.gui.qt_app fvoas_anonymization
```

### Web Interface

```bash
# Using framework's web app (random port)
python -m dsmil_framework.web.react_app
```

### Module Management

```bash
# List modules (should show fvoas_anonymization)
frameworkctl modules list

# Check module status
frameworkctl modules status fvoas_anonymization

# Run module action
frameworkctl modules run fvoas_anonymization --action get_status
```

## Convenience Wrapper (Optional)

If you prefer a convenience wrapper:

```bash
# TUI (uses framework's dsmil command)
python run_fvoas_interface.py

# Qt (uses framework's Qt launcher)
python run_fvoas_interface.py --qt

# Web (uses framework's web app, random port)
python run_fvoas_interface.py --web
```

## Module Registration

The FVOAS module is registered via `setup.py` entry points:

```python
'dsmil.modules': [
    'fvoas_anonymization=audioanalysisx1.fvoas.web_module:FVOASAnonymizationModule',
],
```

This means the module is automatically discovered by the framework when installed.

## Framework Integration

The module properly extends `EngineModuleBase` and:

- ✅ Uses framework's module registry
- ✅ Supports multiple GUI frameworks (TUI, Qt, Web)
- ✅ Uses framework's backend abstraction
- ✅ Follows framework's access control
- ✅ Integrates with framework's configuration system

## Configuration

Configure FVOAS backend in `config/backends.yaml`:

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

## Why Use Framework Commands?

1. **Proper Integration** - Uses framework's module system
2. **Consistent Interface** - Same commands for all modules
3. **Configuration** - Respects framework's config system
4. **Access Control** - Uses framework's AC/TEMPEST system
5. **Plugin Support** - Works with framework plugins
6. **No Port Conflicts** - Framework handles port management

## Deprecated Launcher

`run_fvoas_web.py` is kept for backward compatibility but should not be used. Use `run_fvoas_interface.py` or framework commands directly.

---

**Classification: SECRET | Distribution: Authorized Personnel Only**
