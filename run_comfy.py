import os
import subprocess
import argparse

COMFYUI_PATH = "./ComfyUI"

def run_comfyui(port):
    """Launch ComfyUI with external access."""
    os.chdir(COMFYUI_PATH)
    print(f"🚀 Launching ComfyUI on port {port}...")

    subprocess.run(f"python main.py --listen 0.0.0.0 --port {port} --disable-auto-launch", shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ComfyUI")
    parser.add_argument('--port', type=int, default=8000, help='Port to run ComfyUI on')
    args = parser.parse_args()

    run_comfyui(args.port)
