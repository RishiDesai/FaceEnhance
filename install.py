import os

# Define paths
BASE_PATH = "./ComfyUI"
MODEL_PATH = os.path.join(BASE_PATH, "models")
CACHE_PATH = "/workspace/huggingface_cache"

os.environ["HF_HOME"] = CACHE_PATH
os.makedirs(CACHE_PATH, exist_ok=True)


def run_command(command):
    """Run a shell command using os.system() (simpler than subprocess)."""
    print(f"🔄 Running: {command}")
    exit_code = os.system(command)

    if exit_code != 0:
        print(f"❌ Command failed: {command} (Exit Code: {exit_code})")
        exit(1)  # Exit on failure


def install_dependencies():
    """Install system dependencies and Python packages."""
    print("📦 Installing dependencies...")
    # run_command("apt-get update && apt-get install -y git wget curl libgl1-mesa-glx libglib2.0-0 tmux emacs git-lfs")
    run_command("pip install --upgrade pip")
    run_command("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
    run_command("pip install xformers --index-url https://download.pytorch.org/whl/cu124")
    run_command("pip install -r requirements.txt")
    print("✅ Dependencies installed.")


def manage_git_repo(repo_url, install_path, requirements=False, submodules=False):
    """Clone or update a git repository and handle its dependencies.

    Args:
        repo_url: URL of the git repository
        install_path: Where to install/update the repository
        requirements: Whether to install requirements.txt
        submodules: Whether to update git submodules
    """
    if not os.path.exists(install_path) or not os.path.isdir(install_path) or not os.path.exists(
            os.path.join(install_path, ".git")):
        print(f"📂 Cloning {os.path.basename(install_path)}...")
        run_command(f"git clone {repo_url} {install_path}")
    else:
        print(f"🔄 {os.path.basename(install_path)} exists. Checking for updates...")

    # Change to repo directory and update
    os.chdir(install_path)
    run_command("git pull")

    if submodules:
        run_command("git submodule update --init --recursive")

    if requirements:
        run_command("python -m pip install -r requirements.txt")

    print(f"✅ {os.path.basename(install_path)} installed and updated.")


def install_comfyui():
    """Clone and set up ComfyUI if not already installed."""
    manage_git_repo(
        "https://github.com/comfyanonymous/ComfyUI.git",
        BASE_PATH,
        requirements=True
    )


def download_huggingface_models():
    """Download required models from Hugging Face."""
    from huggingface_hub import hf_hub_download
    hf_models = [
        {"repo_id": "black-forest-labs/FLUX.1-dev", "filename": "flux1-dev.safetensors", "folder": "unet"},
        {"repo_id": "black-forest-labs/FLUX.1-dev", "filename": "ae.safetensors", "folder": "vae"},
        {"repo_id": "Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro", "filename": "diffusion_pytorch_model.safetensors",
         "folder": "controlnet"},
        {"repo_id": "guozinan/PuLID", "filename": "pulid_flux_v0.9.1.safetensors", "folder": "pulid"},
        {"repo_id": "comfyanonymous/flux_text_encoders", "filename": "t5xxl_fp16.safetensors", "folder": "text_encoders"},
        {"repo_id": "comfyanonymous/flux_text_encoders", "filename": "clip_l.safetensors", "folder": "text_encoders"},
    ]

    # Dictionary mapping repo_ids to specific filenames
    filename_mappings = {
        "Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro": "Flux_Dev_ControlNet_Union_Pro_ShakkerLabs.safetensors",
    }

    for model in hf_models:
        try:
            model_path = hf_hub_download(
                repo_id=model["repo_id"], 
                filename=model["filename"],
                cache_dir=CACHE_PATH,
                repo_type=model.get("repo_type", "model")
            )
            target_dir = os.path.join(MODEL_PATH, model["folder"])
            os.makedirs(target_dir, exist_ok=True)

            # Use mapping if it exists, otherwise use original filename
            file_name_only = filename_mappings.get(model["repo_id"], os.path.basename(model["filename"]))
            target_path = os.path.join(target_dir, file_name_only)

            if not os.path.exists(target_path):
                os.symlink(model_path, target_path)
                print(f"✅ Linked: {file_name_only}")
            else:
                print(f"✅ Already exists: {file_name_only}")
        except Exception as e:
            print(f"❌ Failed to download {model['filename']}: {e}")


def download_and_extract_antelopev2():
    """Download and extract AntelopeV2 model for insightface."""
    import zipfile, requests
    base_path = os.path.join(BASE_PATH, "models/insightface/models")
    download_url = "https://huggingface.co/MonsterMMORPG/tools/resolve/main/antelopev2.zip"
    zip_path = os.path.join(base_path, "antelopev2.zip")
    extract_path = os.path.join(base_path, "antelopev2")

    os.makedirs(base_path, exist_ok=True)

    if not os.path.exists(extract_path):
        print(f"📥 Downloading AntelopeV2 model...")
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print("✅ Download complete.")

            print("📂 Extracting AntelopeV2 model...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(base_path)
            print("✅ Extraction complete.")

            os.remove(zip_path)
            print("🗑️ Cleaned up ZIP file.")
        except Exception as e:
            print(f"❌ Failed to download/extract AntelopeV2: {e}")
    else:
        print("✅ AntelopeV2 model already exists")


def install_custom_nodes():
    """Install all custom nodes for ComfyUI."""
    # List of custom nodes to install via comfy node install
    custom_nodes = [
        "comfyui_essentials",
        "comfyui-detail-daemon",
        "comfyui-advancedliveportrait",
        "comfyui-impact-pack",
        "comfyui-custom-scripts",
        "rgthree-comfy",
        "comfyui-easy-use",
        "comfyui-florence2",
        "comfyui-kjnodes",
        "cg-use-everywhere",
        "comfyui-impact-subpack",
        "pulid_comfyui",
        "comfyui_pulid_flux_ll",
        "comfyui_birefnet_ll",
        "comfyui_controlnet_aux"
    ]

    os.chdir(BASE_PATH)
    # First update all existing nodes
    run_command("comfy node update all")

    # Then install any missing nodes
    for node in custom_nodes:
        run_command(f"comfy node install {node}")

    print("✅ Installed and updated all ComfyUI registry nodes.")

    # List of custom nodes to install from git
    custom_nodes_git = [
        {
            "repo": "https://github.com/WASasquatch/was-node-suite-comfyui.git",
            "name": "was-node-suite-comfyui",
            "requirements": True
        },
        {
            "repo": "https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git",
            "name": "ComfyUI_UltimateSDUpscale",
            "submodules": True
        },
        {
            "repo": "https://github.com/huanngzh/ComfyUI-MVAdapter",
            "name": "ComfyUI-MVAdapter",
            "requirements": True
        },
        {
            "repo": "https://github.com/sipie800/ComfyUI-PuLID-Flux-Enhanced.git",
            "name": "ComfyUI-PuLID-Flux-Enhanced",
            "requirements": True
        },
        {
            "repo": "https://github.com/liusida/ComfyUI-AutoCropFaces.git",
            "name": "ComfyUI-AutoCropFaces",
            "submodules": True
        },
        {
            "repo": "https://github.com/giriss/comfy-image-saver.git",
            "name": "comfy-image-saver",
            "requirements": True
        },
        {
            "repo": "https://github.com/spacepxl/ComfyUI-Image-Filters.git",
            "name": "ComfyUI-Image-Filters",
            "requirements": True
        },
        {
            "repo": "https://github.com/pydn/ComfyUI-to-Python-Extension.git",
            "name": "ComfyUI-to-Python-Extension",
            "requirements": True
        },
        {
            "repo": "https://github.com/Limitex/ComfyUI-Diffusers.git",
            "name": "ComfyUI-Diffusers",
            "requirements": True,
            "post_install": [
                "git clone https://github.com/cumulo-autumn/StreamDiffusion.git",
                "python -m streamdiffusion.tools.install-tensorrt"
            ]
        },
        {
            "repo": "https://github.com/Vaibhavs10/ComfyUI-DDUF.git",
            "name": "ComfyUI-DDUF",
            "requirements": True
        },
        {
            "repo": "https://github.com/Chaoses-Ib/ComfyScript.git",
            "name": "ComfyScript",
            "post_install": [
                "python -m pip install -e \".[default]\""
            ]
        }
    ]

    # Install nodes from git
    os.chdir(os.path.join(BASE_PATH, "custom_nodes"))
    for node in custom_nodes_git:
        repo_name = node["name"]
        repo_path = os.path.join(BASE_PATH, "custom_nodes", repo_name)
        manage_git_repo(
            node["repo"],
            repo_path,
            requirements=node.get("requirements", False),
            submodules=node.get("submodules", False)
        )

        # Handle any post-install commands
        if "post_install" in node:
            os.chdir(repo_path)
            for command in node["post_install"]:
                run_command(command)


def install_comfyui_manager():
    """Install ComfyUI Manager."""
    manager_path = os.path.join(BASE_PATH, "custom_nodes", "ComfyUI-Manager")
    manage_git_repo(
        "https://github.com/ltdrdata/ComfyUI-Manager",
        manager_path,
        requirements=True
    )


if __name__ == "__main__":
    # install_dependencies()
    install_comfyui()
    install_comfyui_manager()
    # download_huggingface_models()
    # install_custom_nodes()
    print("🎉 Setup Complete! Run `run.py` to start ComfyUI.")
