import os
import subprocess

COMFYUI_PATH = "./ComfyUI"
PORT = 8000


def run_comfyui():
    """Launch ComfyUI with external access."""
    os.chdir(COMFYUI_PATH)
    print(f"🚀 Launching ComfyUI on port {PORT}...")

    subprocess.run(f"python main.py --listen 0.0.0.0 --port {PORT} --disable-auto-launch", shell=True)


if __name__ == "__main__":
    run_comfyui()
    print(f"Enable port-forwarding\nssh -L {PORT}:localhost:{PORT} [NAME]@[IP_ADDRESS] -p [SERVER_PORT] -i [PRIVATE_KEY]")
