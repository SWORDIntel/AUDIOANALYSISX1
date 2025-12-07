# FVOAS Electron Desktop App

**Classification: SECRET**  
**Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303**

## Overview

Electron wrapper for FVOAS web interface - provides a native desktop app experience without launching a browser.

## Installation

```bash
cd electron_app
npm install
```

## Development

```bash
# Start Electron app (development mode)
npm run dev

# Or directly
electron .
```

## Building

```bash
# Build for current platform
npm run build

# Builds will be in dist/ directory
```

## Features

- ✅ **Native Desktop App** - No browser window
- ✅ **Auto-starts Backend** - Automatically launches FVOAS web server
- ✅ **Random Port** - Uses random port to avoid conflicts
- ✅ **FVOAS Theme** - Dark theme with cyan accents
- ✅ **TEMPEST Support** - TEMPEST toggle integrated
- ✅ **Menu Bar** - Native application menu
- ✅ **Auto-quit** - Stops backend server on exit

## Usage

```bash
# From project root
python run_fvoas_electron.py

# Or directly
cd electron_app
npm start
```

## Platform Support

- ✅ Linux
- ✅ Windows
- ✅ macOS

## Requirements

- Node.js 18+
- npm or yarn
- Python 3.10+ (for backend)
- FVOAS backend dependencies

---

**Classification: SECRET | Distribution: Authorized Personnel Only**
