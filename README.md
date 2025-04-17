# FaceEnhance
Enhancing faces in AI generated images.

<div style="display: flex; justify-content: space-around;">
  <div>
    <h4>Before</h4>
    <img src="examples/chatgpt_elon.png" alt="Elon Before" width="300"/>
  </div>
  <div>
    <h4>After</h4>
    <img src="examples/enhanced_elon.png" alt="Elon After" width="300"/>
  </div>
</div>

## Installation

### Prerequisites
- Python 3.8 or higher
- 1 GPU with 48GB VRAM
- At least 50GB of free disk space

### Setup

1. Set up your Hugging Face token:
   - Create a token at [Hugging Face](https://huggingface.co/settings/tokens)
   - Set the token as an environment variable. HuggingFace requires login for downloading Flux:
     ```
     export HUGGINGFACE_TOKEN=your_token_here
     export HF_HOME=/path/to/your/huggingface_cache
     ```
   - Models will be downloaded to `$HF_HOME` and then symlinked to `./ComfyUI/models/`

2. Create the virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Run the install script:
   ```
   python install.py
   ```

This will
- Install ComfyUI, custom nodes, and required dependencies to your venv
- Download all required models (Flux.1-dev, ControlNet, text encoders, PuLID, and more)

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

### Notes
- The script and demo run a ComfyUI server ephemerally
- All images are saved in ./ComfyUI/input/scratch/
- Temporary files are created during processing and cleaned up afterward
