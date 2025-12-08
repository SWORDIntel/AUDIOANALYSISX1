# Multi-Device Setup Guide - 1000+ TOPS Configuration

## Overview

This guide explains how to configure the system for maximum performance using multiple Intel devices combined with DMA shared memory to achieve **1000+ TOPS**.

## Hardware Requirements

### Required Components

1. **2x Intel Movidius Neural Compute Sticks (VPU)**
   - Intel Neural Compute Stick 2 (NCS2)
   - USB 3.0+ connection
   - ~4 TOPS each = ~8 TOPS combined

2. **Intel Arc GPU**
   - Intel Arc A-series graphics card
   - ~200 TOPS
   - PCIe connection

3. **Intel CPU**
   - Intel Xeon or Core processor
   - DMA support enabled
   - ~50+ TOPS with optimized processing

4. **System Requirements**
   - Linux kernel 5.4+ (recommended)
   - USB 3.0+ ports (2x for VPU sticks)
   - PCIe slot for GPU
   - Sufficient power supply

## Installation Steps

### Step 1: Install Movidius VPU Drivers

```bash
# Download Intel Neural Compute Stick 2 drivers
wget https://download.01.org/opencv/2021/openvinotoolkit/2021.4/l_openvino_toolkit_ubuntu20_2021.4.582.tgz

# Extract and install
tar -xzf l_openvino_toolkit_ubuntu20_2021.4.582.tgz
cd l_openvino_toolkit_ubuntu20_2021.4.582
sudo ./install.sh

# Install USB rules
sudo usermod -a -G users "$(whoami)"
```

### Step 2: Verify VPU Detection

```bash
# Check USB devices
lsusb | grep -i movidius

# Expected output (2 devices):
# Bus 003 Device 004: ID 03e7:2485 Intel Movidius MyriadX
# Bus 003 Device 005: ID 03e7:2485 Intel Movidius MyriadX

# Verify OpenVINO can see VPUs
python3 -c "from openvino.runtime import Core; c=Core(); print(c.available_devices)"
# Should show: ['CPU', 'VPU.0', 'VPU.1']
```

### Step 3: Install Intel Arc GPU Drivers

```bash
# Add Intel graphics repository
wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | sudo apt-key add -
sudo add-apt-repository 'deb [arch=amd64] https://repositories.intel.com/gpu/ubuntu focal main'
sudo apt update

# Install Intel graphics drivers
sudo apt install intel-opencl-icd intel-level-zero-gpu level-zero intel-media-va-driver-non-free

# Verify GPU detection
lspci | grep -i vga
# Should show Intel Arc GPU
```

### Step 4: Configure DMA Shared Memory

```bash
# Check DMA support
dmesg | grep -i dma
# Should show DMA controllers

# Verify shared memory support
cat /proc/meminfo | grep -i shared
# Should show shared memory available

# Set shared memory size (if needed)
# Edit /etc/fstab or use tmpfs
sudo mount -t tmpfs -o size=2G tmpfs /dev/shm
```

### Step 5: Install OpenVINO with Multi-Device Support

```bash
# Install OpenVINO
pip install openvino openvino-dev

# Verify installation
python3 -c "from openvino.runtime import Core; c=Core(); print('Devices:', c.available_devices)"
```

## Configuration

### Automatic Configuration (Recommended)

The system automatically detects and configures multi-device setup:

```python
from audioanalysisx1.fvoas import FVOASController

# Auto-detect and configure multi-device
with FVOASController(enable_ml=True, ml_device="AUTO") as fvoas:
    stats = fvoas.get_stats()
    ml_stats = stats.get('ml', {})
    
    print(f"Device Configuration: {ml_stats.get('device')}")
    print(f"Devices: {ml_stats.get('devices', [])}")
    print(f"Estimated TOPS: {ml_stats.get('estimated_tops')}")
    print(f"DMA Shared Memory: {ml_stats.get('dma_shared_memory', False)}")
```

### Manual Configuration

```python
# Explicitly specify multi-device configuration
with FVOASController(
    enable_ml=True,
    ml_device="MULTI:VPU.0,VPU.1,GPU,CPU"
) as fvoas:
    # System will use:
    # - VPU.0: First Movidius stick
    # - VPU.1: Second Movidius stick
    # - GPU: Intel Arc GPU
    # - CPU: Intel CPU with DMA
    pass
```

## Verification

### Check Device Detection

```python
from audioanalysisx1.fvoas import check_openvino_availability

status = check_openvino_availability()
print("Available Devices:", status['devices'])

# Should show: ['CPU', 'VPU.0', 'VPU.1', 'GPU']
```

### Benchmark Performance

```python
from audioanalysisx1.fvoas.benchmark_ml import run_benchmark

# Run benchmark on multi-device configuration
results = run_benchmark(num_iterations=100)

# Expected performance:
# - Throughput: 500-2000 fps
# - Latency: 1-2ms
# - TOPS Utilization: 85-95%
```

### Monitor TOPS Utilization

```python
with FVOASController(enable_ml=True) as fvoas:
    # Process some audio
    fvoas.set_preset('anonymous_moderate')
    
    # Get performance stats
    stats = fvoas.get_stats()
    ml_stats = stats.get('ml', {})
    
    print(f"Actual TOPS: {ml_stats.get('actual_tops', 0)}")
    print(f"TOPS Utilization: {ml_stats.get('tops_utilization_percent', 0)}%")
    print(f"Throughput: {ml_stats.get('throughput_fps', 0)} fps")
```

## Performance Optimization

### 1. Enable INT8 Precision

```python
# Use INT8 models for maximum performance
# INT8 provides 2-4x speedup over FP32
modifier = OpenVINOVoiceModifier(
    model_path="/path/to/int8_model.xml",
    device="MULTI:VPU.0,VPU.1,GPU,CPU",
    precision="INT8"
)
```

### 2. Increase Batch Size

```python
# Larger batches utilize more TOPS
modifier = OpenVINOVoiceModifier(
    batch_size=32,  # Process 32 audio chunks simultaneously
    num_streams=4   # 4 parallel inference streams
)
```

### 3. Optimize Load Balancing

The system automatically balances workload:
- **VPUs**: Handle initial feature extraction
- **GPU**: Handles complex neural network layers
- **CPU**: Coordinates and handles post-processing

### 4. DMA Shared Memory Benefits

- **Zero-copy transfers**: Data shared directly between devices
- **Reduced latency**: No memory copying overhead
- **Higher throughput**: Parallel processing without bottlenecks

## Troubleshooting

### VPU Not Detected

```bash
# Check USB connection
lsusb | grep -i movidius

# Check USB permissions
sudo chmod 666 /dev/bus/usb/*/*

# Reload USB drivers
sudo modprobe -r usbcore
sudo modprobe usbcore
```

### GPU Not Available

```bash
# Check GPU detection
lspci | grep -i vga

# Verify OpenVINO GPU support
python3 -c "from openvino.runtime import Core; c=Core(); print('GPU' in c.available_devices)"
```

### Low TOPS Utilization

1. **Check batch size**: Increase `batch_size` parameter
2. **Verify DMA**: Ensure shared memory is properly configured
3. **Check model precision**: Use INT8 for maximum performance
4. **Monitor device load**: Ensure all devices are being utilized

### Performance Issues

```python
# Enable profiling to identify bottlenecks
modifier = OpenVINOVoiceModifier(
    enable_profiling=True
)

# Check profiling data
stats = modifier.get_stats()
profiling = stats.get('profiling_data', [])
```

## Expected Performance

With proper configuration:

- **Combined TOPS**: 1000+ TOPS
- **Throughput**: 500-2000 fps
- **Latency**: 1-2ms per inference
- **TOPS Utilization**: 85-95%
- **Memory Bandwidth**: Maximized with DMA shared memory

## References

- [Intel Movidius NCS2 Documentation](https://www.intel.com/content/www/us/en/developer/tools/neural-compute-stick/overview.html)
- [Intel Arc GPU Documentation](https://www.intel.com/content/www/us/en/products/docs/discrete-gpus/arc/desktop/a-series/overview.html)
- [OpenVINO Multi-Device Inference](https://docs.openvino.ai/latest/openvino_docs_OV_UG_supported_plugins_MULTI.html)
