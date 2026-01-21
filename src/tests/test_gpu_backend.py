
import sys
import os

try:
    import torch
except ImportError:
    print("❌ Torch not installed.")
    sys.exit(1)

def check_gpu_backend():
    print(f"[*] Torch Version: {torch.__version__}")
    
    # 1. Check CUDA
    if torch.cuda.is_available():
        print(f"✅ Backend: CUDA")
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        return
        
    # 2. Check DirectML
    try:
        import torch_directml
        device = torch_directml.device()
        print(f"✅ Backend: DirectML")
        print(f"   Device ID: {torch_directml.device_name(0)}")
        
        # Test Memory Op
        print("   Testing Memory Op on DML...", end="")
        t = torch.tensor([1, 2, 3]).to(device)
        print(" OK")
        return
    except ImportError:
        pass
        
    # 3. Fallback CPU
    print("⚠️  Backend: CPU (No GPU Acceleration Detected)")
    print("   Note: For AMD GPUs on Windows, install 'torch-directml'.")

if __name__ == "__main__":
    check_gpu_backend()
