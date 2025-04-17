# Face Enhance
A tool for improving facial consistency and quality in AI-generated images. Dramatically enhance facial fidelity while preserving the original image's background, lighting, and composition.

<div style="text-align: center;">
  <img src="examples/elon_compare.gif" alt="Elon Comparison" width="600"/>
</div>

## Installation

### Prerequisites
- Python 3.11 or higher
- 1 GPU with 48GB VRAM
- At least 50GB of free disk space

### Setup

1. Set up your Hugging Face token:
   - Create a token at [Hugging Face](https://huggingface.co/settings/tokens)
   - Set the following environment variables:
     ```
     export HUGGINGFACE_TOKEN=your_token_here
     export HF_HOME=/path/to/your/huggingface_cache
     ```
   - Models will be downloaded to `$HF_HOME` and then symlinked to `./ComfyUI/models/`
   - Hugging Face requires login for downloading Flux

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

## Running on ComfyUI

Using the ComfyUI workflows is the fastest way to get started. Run `python run_comfy.py`
- `./workflows/FaceEnhancementProd.json` for face enhancement
- `./workflows/FaceEmbedDist.json` for computing the face embed distance


## Configuration

Create a .env file in the project root directory with your API keys:
```
touch .env
echo "FAL_API_KEY=your_fal_api_key_here" >> .env
```

The FAL API key is used for face upscaling during preprocessing. You can get one at [fal.ai](https://fal.ai/).

# Gradio Demo

A simple web interface for the face enhancement workflow. 

1. Run

```bash
python gradio_demo.py
```
2. Go to http://localhost:7860. You may need to enable port forwarding.

### Notes
- The script and demo run a ComfyUI server ephemerally
- All images are saved in ./ComfyUI/input/scratch/
- Temporary files are created during processing and cleaned up afterward

### Troubleshooting

- **Out of memory errors**: If your GPU has less than 48 GB VRAM, install [Flux.1-dev at float8 precision](https://huggingface.co/Comfy-Org/flux1-dev).
- **Face detection issues**: This method works for photorealistic images of people. It may not work on cartoons, anime characters, or non-human subjects.
- **Downloading models fails**: Check your Hugging Face token has proper permissions.
