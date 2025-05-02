import os

COMFYUI_PATH = "./ComfyUI"


def run_cmd(command):
    """Run a shell command"""
    print(f"🔄 Running: {command}")
    exit_code = os.system(command)
    if exit_code != 0:
        print(f"❌ Command failed: {command} (Exit Code: {exit_code})")
        exit(1)


def install_lfs_files():
    """Install dependencies, pull git lfs files."""
    run_cmd("apt-get update && apt-get install -y git-lfs")
    hook_path = os.path.join(".git", "hooks", "pre-push")
    if os.path.exists(hook_path):
        print("⚠️ Git LFS hook already exists. Skipping installation.")
    else:
        run_cmd("git lfs install")
    
    run_cmd("git lfs pull")
    print("✅ Git LFS installed and files pulled.")


def install_git_repo(repo_url, install_path, requirements=False, submodules=False):
    """Clone or update a git repository and handle its dependencies"""
    original_dir = os.getcwd()

    if not os.path.exists(install_path) or not os.path.isdir(install_path) or not os.path.exists(
            os.path.join(install_path, ".git")):
        print(f"📂 Cloning {os.path.basename(install_path)}...")
        run_cmd(f"git clone {repo_url} {install_path}")
    else:
        print(f"🔄 {os.path.basename(install_path)} exists. Checking for updates...")

    # Change to repo directory and update
    os.chdir(install_path)
    run_cmd("git pull")

    if submodules:
        run_cmd("git submodule update --init --recursive")
    if requirements:
        run_cmd("python -m pip install -r requirements.txt")

    print(f"✅ {os.path.basename(install_path)} installed and updated.")
    os.chdir(original_dir)


def install_comfyui():
    """Clone and set up ComfyUI if not already installed."""
    install_git_repo(
        "https://github.com/comfyanonymous/ComfyUI.git",
        COMFYUI_PATH,
        requirements=True
    )


def download_huggingface_models():
    """Download required models from Hugging Face and symlink to ComfyUI models directory."""
    from huggingface_hub import hf_hub_download
    hf_models = [
        # {"repo_id": "black-forest-labs/FLUX.1-dev", "filename": "flux1-dev.safetensors", "folder": "unet"},
        {"repo_id": "black-forest-labs/FLUX.1-dev", "filename": "ae.safetensors", "folder": "vae"},
        {"repo_id": "Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro", "filename": "diffusion_pytorch_model.safetensors",
         "folder": "controlnet"},
        {"repo_id": "guozinan/PuLID", "filename": "pulid_flux_v0.9.1.safetensors", "folder": "pulid"},
        {"repo_id": "comfyanonymous/flux_text_encoders", "filename": "t5xxl_fp16.safetensors",
         "folder": "text_encoders"},
        {"repo_id": "comfyanonymous/flux_text_encoders", "filename": "clip_l.safetensors", "folder": "text_encoders"},
    ]

    # More specific filenames
    filename_mappings = {
        "Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro": "Flux_Dev_ControlNet_Union_Pro_ShakkerLabs.safetensors",
    }

    for model in hf_models:
        try:
            model_path = hf_hub_download(
                repo_id=model["repo_id"],
                filename=model["filename"],
                cache_dir=os.getenv('HF_HOME'),
                repo_type=model.get("repo_type", "model"),
                token=os.getenv('HUGGINGFACE_TOKEN')
            )
            target_dir = os.path.join(COMFYUI_PATH, "models", model["folder"])
            os.makedirs(target_dir, exist_ok=True)

            # Use mapping if it exists, otherwise use original filename
            file_name_only = filename_mappings.get(model["repo_id"], os.path.basename(model["filename"]))
            target_path = os.path.join(target_dir, file_name_only)

            if not os.path.exists(target_path):
                os.symlink(model_path, target_path)
                print(f"✅ Linked: {model_path} to {target_path}")
            else:
                print(f"✅ Already exists: {file_name_only}")
        except Exception as e:
            print(f"❌ Failed to download {model['filename']}: {e}")


def download_and_extract_antelopev2():
    """Download and extract AntelopeV2 model for insightface."""
    import zipfile, requests, shutil

    base_path = os.path.join(COMFYUI_PATH, "models", "insightface/models")
    model_target_path = os.path.join(base_path, "antelopev2")
    download_url = "https://huggingface.co/MonsterMMORPG/tools/resolve/main/antelopev2.zip"
    zip_path = os.path.join(base_path, "antelopev2.zip")
    temp_extract_path = os.path.join(base_path, "temp_antelopev2")

    os.makedirs(base_path, exist_ok=True)

    if not os.path.exists(model_target_path) or not os.listdir(model_target_path):
        # First, remove any existing problematic directories
        if os.path.exists(model_target_path):
            shutil.rmtree(model_target_path)

        print(f"📥 Downloading AntelopeV2 model...")
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(zip_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print("✅ Download complete.")

            # Create a temporary extraction directory
            os.makedirs(temp_extract_path, exist_ok=True)

            print("📂 Extracting AntelopeV2 model...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_extract_path)
            print("✅ Extraction complete.")

            # Create the target directory
            os.makedirs(model_target_path, exist_ok=True)

            # Move the model files to the correct location
            # The ZIP contains a nested antelopev2 directory we need to move files from
            nested_model_dir = os.path.join(temp_extract_path, "antelopev2")
            if os.path.exists(nested_model_dir):
                for item in os.listdir(nested_model_dir):
                    source = os.path.join(nested_model_dir, item)
                    target = os.path.join(model_target_path, item)
                    shutil.move(source, target)

            # Clean up
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path)
            if os.path.exists(zip_path):
                os.remove(zip_path)

            print("🗑️ Cleaned up temporary files.")
            print("✅ AntelopeV2 model installed correctly.")

        except Exception as e:
            print(f"❌ Failed to download/extract AntelopeV2: {e}")
    else:
        print("✅ AntelopeV2 model already exists")


def install_custom_nodes():
    """Install all custom nodes for ComfyUI."""

    custom_nodes = [
        {
            "repo": "https://github.com/sipie800/ComfyUI-PuLID-Flux-Enhanced",
            "name": "ComfyUI-PuLID-Flux-Enhanced",
            "requirements": True
        },
        {
            "repo": "https://github.com/rgthree/rgthree-comfy",
            "name": "rgthree-comfy",
            "requirements": True
        },
        {  # we already have insightface so don't need requirements (no dlib)
            "repo": "https://github.com/cubiq/ComfyUI_FaceAnalysis",
            "name": "ComfyUI_FaceAnalysis",
            "requirements": False
        },
    ]

    for node in custom_nodes:
        repo_name = node["name"]
        repo_path = os.path.join(COMFYUI_PATH, "custom_nodes", repo_name)
        install_git_repo(
            node["repo"],
            repo_path,
            requirements=node.get("requirements", False),
            submodules=node.get("submodules", False)
        )
        print(f"✅ {repo_name} installed and updated.")

    print("✅ Installed and updated all ComfyUI nodes.")


def install_hfdemo_dependencies():
    """Some steps specific to HF (ZeroGPU) spaces"""
    run_cmd("python -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124")
    run_cmd("python -m pip install -r requirements.txt")

    # If we're using persistent storage, change to "/data/huggingface_cache"
    HF_CACHE = "./huggingface_cache"
    os.environ['HF_HOME'] = HF_CACHE
    os.makedirs(HF_CACHE, exist_ok=True)


def install(is_hf_space=False):
    install_lfs_files()
    install_comfyui()
    install_custom_nodes()
    if is_hf_space:
        print("🔄 Installing HF spaces dependencies...")
        install_hfdemo_dependencies()
    download_huggingface_models()
    download_and_extract_antelopev2()
    print("🎉 Setup Complete!")

if __name__ == "__main__":
    install()
