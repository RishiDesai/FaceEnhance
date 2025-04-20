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
- At least 60GB of free disk space

### Setup

1. Set up your Hugging Face token:
   - Create a token at [Hugging Face](https://huggingface.co/settings/tokens)
   - Log into Hugging Face and accept their terms of service to download [Flux.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)
   - Set the following environment variables:
     ```
     export HUGGINGFACE_TOKEN=your_token_here
     export HF_HOME=/path/to/your/huggingface_cache
     ```
   - Models will be downloaded to `$HF_HOME` and symlinked to `FaceEnhance/ComfyUI/models/`

2. Create the virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   <details>
   <summary>If you want a specific PyTorch+CUDA version</summary>

   ```bash
   python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   python -m pip install xformers --index-url https://download.pytorch.org/whl/cu124
   ```

   </details>

3. Run the install script:
   ```
   python install.py
   ```

   This will
   - Install ComfyUI, custom nodes, and remaining dependencies to your venv
   - Download all required models (Flux.1-dev, ControlNet, text encoders, PuLID, and more)

4. Run inference on one example:

   ```
   python test.py --input examples/dany_gpt_1.png --ref examples/dany_face.jpg --out examples/dany_enhanced.png
   ```

   <details>
   <summary>Arguments</summary>

   - `--input` (str): Path to the input image.
   - `--ref` (str): Path to the reference face image.
   - `--output` (str): Path to save the output image.
   - `--id_weight` (float): Face ID weight. Default: 0.75.
   </details>

## Gradio Demo

A simple web interface for the face enhancement workflow. 

1. Run `python demo.py`

2. Go to http://localhost:7860. You may need to enable port forwarding.

## Running on ComfyUI

Run `python run_comfy.py`. There are two workflows:
- `FaceEnhance/workflows/FaceEnhancementProd.json` for face enhancement
- `FaceEnhance/workflows/FaceEmbedDist.json` for computing the [face embedding distance](https://github.com/cubiq/ComfyUI_FaceAnalysis)


### Notes
- The script and demo run a ComfyUI server ephemerally
- Gradio demo is faster than the script because the models remain loaded in memory and ComfyUI server is booted up.
- Images are saved in `FaceEnhance/ComfyUI/input/scratch/`
- `FaceEnhancementProd.py` was created with the [ComfyUI-to-Python-Extension](https://github.com/pydn/ComfyUI-to-Python-Extension) and re-engineered for efficiency and function.
- Face cropping, upscaling, and captioning are unavailable; these will be added in an update.

### Troubleshooting

- **Out of memory errors**: If your GPU has less than 48 GB VRAM, install [Flux.1-dev at fp8 precision](https://huggingface.co/Comfy-Org/flux1-dev).
- **Face detection issues**: This method works for photorealistic images of people. It may not work on cartoons, anime characters, or non-human subjects.
- **Downloading models fails**: Check your Hugging Face token has proper permissions.
