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
   This defines where models will be downloaded and then symlinked to the ComfyUI folder.

3. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies from requirements.txt:
   ```
   pip install -r requirements.txt
   ```

5. Run the installation script:
   ```
   python install.py
   ```

This script will:
- Install all required dependencies to your venv
- Install ComfyUI and necessary custom nodes
- Download and install all required models (FLUX, ControlNet, text encoders, PuLID, and more)

## Configuration

Create a .env file in the project root directory with your API keys:
```
touch .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
echo "FAL_API_KEY=your_fal_api_key_here" >> .env
```

These API keys are required for certain features of the application to work properly.

# Face Enhancement Gradio Demo

A web interface for the face enhancement workflow using Gradio.

## Features

- Simple web interface for face enhancement
- Upload input image and reference face image
- Queue system to process jobs sequentially on a single GPU
- Approximately 60 seconds processing time per image

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Gradio demo:

```bash
python gradio_demo.py
```

3. Open your browser and go to http://localhost:7860

## Usage

1. Upload an input image you want to enhance
2. Upload a reference face image
3. Click "Enhance Face" to start the process
4. Wait approximately 60 seconds for processing
5. View the enhanced result in the output panel

## Notes

- The demo uses a job queue to ensure only one job runs at a time
- Processing takes approximately 60 seconds per image
- Temporary files are created during processing and cleaned up afterward
