# FaceEnhance
Enhancing faces in AI generated images.

## Installation

### Prerequisites
- Python 3.8 or higher
- At least 50GB of free disk space for models and dependencies

### Setup

1. Set up your Hugging Face token:
   - Create a token at [Hugging Face](https://huggingface.co/settings/tokens) if you don't have one
   - Set the token as an environment variable:
     ```
     export HUGGINGFACE_TOKEN=your_token_here
     ```

2. Set the Hugging Face cache directory:
   ```
   export HF_HOME=/path/to/your/huggingface_cache
   ```
   This defines where models will be downloaded and later symlinked to the ComfyUI folder.

3. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Run the installation script:
   ```
   python install.py
   ```

This script will:
- Install all required dependencies to your virtual environment
- Install ComfyUI and necessary custom nodes
- Download and install all required models (FLUX, ControlNet, text encoders, PuLID, and more)
