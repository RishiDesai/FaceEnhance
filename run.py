import os
import subprocess

BASE_PATH = "./ComfyUI"
PORT = 8000

def run_comfyui():
    """Launch ComfyUI with external access."""
    os.chdir(BASE_PATH)
    print(f"🚀 Launching ComfyUI on port {PORT}...")

    subprocess.run(f"python main.py --listen 0.0.0.0 --port {PORT} --disable-auto-launch", shell=True)

if __name__ == "__main__":
    run_comfyui()
    print(f"Now run port-forwarding\nssh -L {PORT}:localhost:{PORT} root@[IP address] -p [RUNPOD_PORT] -i ~/.ssh/id_runpod")
