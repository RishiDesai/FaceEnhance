# FaceEnhance
Enhancing faces in AI generated images.

## Installation

### Prerequisites
- Python 3.8 or higher
- 1 GPU with 48GB VRAM
- At least 50GB of free disk space

### Setup

1. Set up your Hugging Face token:
   - Create a token at [Hugging Face](https://huggingface.co/settings/tokens) set it as an environment variable.
   - Set the token as an environment variable. HuggingFace requires login for downloading Flux:
     ```
     export HUGGINGFACE_TOKEN=your_token_here
     ```
    - Set the Hugging Face cache directory:
      ```
      export HF_HOME=/path/to/your/huggingface_cache
      ```
      Models will be downloaded here and then symlinked to ./ComfyUI/models/.

2. Create virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Run installation script:
   ```
   python install.py
   ```

This script will:
- Install all required dependencies to your venv
- Install ComfyUI and required custom nodes
- Download and install all required models (Flux.1-dev, ControlNet, text encoders, PuLID, and more)

## Configuration

Create a .env file in the project root directory with your API keys:
```
touch .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
echo "FAL_API_KEY=your_fal_api_key_here" >> .env
```

These API keys are required for certain features of the application to work properly.

# Gradio Demo

A web interface for the face enhancement workflow. 

1. Run

```bash
python gradio_demo.py
```

2. Run this on a separate terminal for port-forwarding 
```bash
ssh -L 7860:localhost:7860 root@[IP_ADDRESS] -p [SERVER_PORT] -i [PRIVATE_KEY]
```

3. Go to http://localhost:7860

## Usage

1. Upload an input image you want to enhance
2. Upload a high-quality reference face image
3. Click "Enhance Face" to start the process
4. Wait approximately 60 seconds for processing
5. View the enhanced result in the output panel

## Notes

- The script runs a ComfyUI server ephemerally
- All images are saved in ./ComfyUI/input/scratch/
- Temporary files are created during processing and cleaned up afterward
