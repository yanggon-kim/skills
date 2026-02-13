# Environment Setup

## 1. Verify Current Machine

Before starting any project, confirm the hardware and tool versions. These were accurate at skill creation time but may change.

```bash
# GPU
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv

# CUDA compiler
nvcc --version

# Profiling tools
nsys --version
ncu --version

# Python
python3 --version

# OS
uname -r && cat /etc/os-release | head -4
```

**Known machine state (at skill creation):**
- GPU: RTX 4070 Ti SUPER, 16 GB, Ada Lovelace (CC 8.9), 66 SMs
- Driver: 580.95.05
- CUDA: 13.0
- NSight Systems: 2025.3.2
- NSight Compute: 2025.3.1.0
- Python: 3.10.12
- OS: Ubuntu 22.04.5 LTS

## 2. Create Virtual Environment

```bash
python3 -m venv /path/to/project/venv
source /path/to/project/venv/bin/activate
```

## 3. Install PyTorch with CUDA

```bash
# Check CUDA version first
nvcc --version

# Install PyTorch matching your CUDA version
# For CUDA 12.4+:
pip install torch torchvision torchaudio

# Verify:
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"
```

**IMPORTANT**: The PyTorch CUDA version must match the system's nvcc version. Mismatches cause `CUDA error: no kernel image is available for execution on the device`.

## 4. Install Model-Specific Dependencies

```bash
# Clone the model/workload repo
git clone <REPO_URL> models/<repo_name>

# Install in editable mode WITHOUT dependencies to avoid conflicts
pip install --no-deps -e models/<repo_name>

# Then install remaining dependencies manually
pip install transformers accelerate pillow numpy matplotlib
```

**Why `--no-deps`?** Model repos often pin old dependency versions that conflict with your PyTorch installation. Install the model package first, then add dependencies one at a time.

## 5. Install flash-attn (Common Pain Point)

Many transformer models require flash-attn. It is a compiled CUDA extension that frequently fails to build.

```bash
# Step 1: Install wheel first
pip install wheel

# Step 2: Install with --no-build-isolation
pip install flash-attn --no-build-isolation

# This compiles from source — takes 5-15 minutes.
# If it fails:
#   - Check that nvcc version matches torch CUDA version
#   - Ensure enough disk space (~5 GB temp)
#   - Try pinning version: pip install flash-attn==2.7.4.post1 --no-build-isolation
```

**Why `--no-build-isolation`?** Without it, pip creates a clean build environment that doesn't have torch installed, causing `ModuleNotFoundError: No module named 'torch'`.

## 6. Verify Profiling Tools Are Accessible

```bash
# NSight Systems
nsys --version
# If not found, check: /usr/local/cuda/bin/nsys

# NSight Compute
ncu --version
# If not found, check: /usr/local/cuda/bin/ncu

# NCU may require elevated permissions on some systems
# If you get "ERR_NVGPUCTRPERM", see:
#   https://developer.nvidia.com/ERR_NVGPUCTRPERM
# Quick fix: sudo sh -c 'echo 1 > /proc/sys/kernel/perf_event_paranoid'
```

## 7. Verify Workload Runs Correctly

Before any profiling, always run the workload once to confirm it works:

```python
import torch

# Load your model
model = ...  # Your model loading code
model.eval().to(device="cuda", dtype=torch.bfloat16)

# Create dummy input matching expected format
dummy_input = torch.randn(1, ..., device="cuda", dtype=torch.bfloat16)

# Run one inference
with torch.inference_mode():
    output = model(dummy_input)

print(f"Inference OK. Output shape: {output.shape}")
print(f"GPU memory used: {torch.cuda.max_memory_allocated() / 1e6:.1f} MB")
```

## 8. Download Model Weights

```bash
# HuggingFace models
pip install huggingface-hub
huggingface-cli download <org>/<model-name> --local-dir models/weights/<model-name>

# Python alternative:
# from huggingface_hub import snapshot_download
# snapshot_download("<org>/<model-name>", local_dir="models/weights/<model-name>")
```

## 9. Prior Project Reference

A complete example of environment setup for a VLA (Vision-Language-Action) model profiling project is at `/home/vortex/dir_yanggon/01_VLA/`. That project used:

| Package | Version |
|---------|---------|
| PyTorch | 2.7.1 |
| CUDA | 13.0 |
| flash-attn | 2.7.4.post1 |
| transformers | 4.51.3 |

See `examples/vla_case_study.md` for the full walkthrough.
