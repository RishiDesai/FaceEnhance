---
title: My Face Enhancement Space
emoji: 😊
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.25.2
app_file: demo.py
pinned: false
---

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
   - Log into Hugging Face and accept their terms of service to download Flux
   - Set the following environment variables:
     ```
     export HUGGINGFACE_TOKEN=your_token_here
     export HF_HOME=/path/to/your/huggingface_cache
     ```
   - Models will be downloaded to `$HF_HOME` and symlinked to `./ComfyUI/models/`

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

4. Run inference on one example:

   ```
   python main.py --input examples/dany_gpt_1.png --ref examples/dany_face.jpg --out examples/dany_enhanced.png
   ```

## Running on ComfyUI

Using the ComfyUI workflows is the fastest way to get started. Run `python run_comfy.py`
- `./workflows/FaceEnhancementProd.json` for face enhancement
- `./workflows/FaceEmbedDist.json` for computing the face embedding distance


## Gradio Demo

A simple web interface for the face enhancement workflow. 

1. Run `python demo.py`

2. Go to http://localhost:7860. You may need to enable port forwarding.

### Notes
- The script and demo run a ComfyUI server ephemerally
- Gradio demo is faster than the script because models remain loaded in memory
- All images are saved in `./ComfyUI/input/scratch/`
- Temporary files are created during processing and cleaned up afterward
- Face cropping and upscaling are not applied to the reference image; this will be added in an update.

### Troubleshooting

- **Out of memory errors**: If your GPU has less than 48 GB VRAM, install [Flux.1-dev at float8 precision](https://huggingface.co/Comfy-Org/flux1-dev).
- **Face detection issues**: This method works for photorealistic images of people. It may not work on cartoons, anime characters, or non-human subjects.
- **Downloading models fails**: Check your Hugging Face token has proper permissions.