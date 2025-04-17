import os
import torch
import numpy as np
from PIL import Image
import sys
import cv2
import base64
import aiohttp
import fal_client
sys.path.append('./ComfyUI_AutoCropFaces')
from dotenv import load_dotenv
load_dotenv()
from Pytorch_Retinaface.pytorch_retinaface import Pytorch_RetinaFace
from transformers import AutoProcessor, AutoModelForCausalLM
from transformers import CLIPProcessor, CLIPModel
import gc


CACHE_DIR = '/workspace/huggingface_cache'

os.environ["HF_HOME"] = CACHE_DIR
os.makedirs(CACHE_DIR, exist_ok=True)

device = "cuda"

def clear_cuda_memory():
    """Aggressively clear CUDA memory"""
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()


def load_vision_models():
    print("Loading CLIP and Florence models...")
    # Load CLIP
    clip_model = CLIPModel.from_pretrained(
        "openai/clip-vit-large-patch14",
        cache_dir=CACHE_DIR
    ).to(device)
    clip_processor = CLIPProcessor.from_pretrained(
        "openai/clip-vit-large-patch14",
        cache_dir=CACHE_DIR
    )

    # Load Florence
    florence_model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Florence-2-large",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
        cache_dir=CACHE_DIR
    ).to(device)
    florence_processor = AutoProcessor.from_pretrained(
        "microsoft/Florence-2-large",
        trust_remote_code=True,
        cache_dir=CACHE_DIR
    )

    return {
        'clip_model': clip_model,
        'clip_processor': clip_processor,
        'florence_model': florence_model,
        'florence_processor': florence_processor,
    }


def generate_caption(image):
    vision_models = load_vision_models()
    
    # Ensure the image is a PIL Image
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)

    # Convert the image to RGB if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    prompt = "<DETAILED_CAPTION>"
    inputs = vision_models['florence_processor'](
        text=prompt,
        images=image,
        return_tensors="pt"
    ).to(device, torch.float16 if torch.cuda.is_available() else torch.float32)

    generated_ids = vision_models['florence_model'].generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        num_beams=3,
        do_sample=False
    )
    generated_text = vision_models['florence_processor'].batch_decode(generated_ids, skip_special_tokens=True)[0]
    parsed_answer = vision_models['florence_processor'].post_process_generation(
        generated_text, task="<DETAILED_CAPTION>",
        image_size=(image.width, image.height)
    )
    
    clear_cuda_memory()
    return parsed_answer['<DETAILED_CAPTION>']


def crop_face(image_path, output_dir, output_name, scale_factor=4.0):
    image = Image.open(image_path).convert("RGB")

    img_raw = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_raw = img_raw.astype(np.float32)

    rf = Pytorch_RetinaFace(
        cfg='mobile0.25',
        pretrained_path='./weights/mobilenet0.25_Final.pth',
        confidence_threshold=0.02,
        nms_threshold=0.4,
        vis_thres=0.6
    )

    dets = rf.detect_faces(img_raw)
    print("Dets: ", dets)
    
    # Instead of asserting, handle multiple faces gracefully
    if len(dets) == 0:
        print("No faces detected!")
        return False
    
    # If multiple faces detected, use the one with highest confidence
    if len(dets) > 1:
        print(f"Warning: {len(dets)} faces detected, using the one with highest confidence")
        # Assuming dets is a list of [bbox, landmark, score] and we want to sort by score
        dets = sorted(dets, key=lambda x: x[2], reverse=True)  # Sort by confidence score
        # Just keep the highest confidence detection
        dets = [dets[0]]

    # Pass the scale_factor to center_and_crop_rescale for adjustable crop size
    try:
        # Unpack the tuple correctly - the function returns (cropped_imgs, bbox_infos)
        cropped_imgs, bbox_infos = rf.center_and_crop_rescale(img_raw, dets, shift_factor=0.45, scale_factor=scale_factor)
        
        # Check if we got any cropped images
        if not cropped_imgs or len(cropped_imgs) == 0:
            print("No cropped images returned")
            return False
        
        # Use the first cropped face image directly - it's not nested
        img_to_save = cropped_imgs[0]
        
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, output_name), img_to_save)
        print(f"Saved: {output_name}")
        return True
        
    except Exception as e:
        print(f"Error during face cropping: {e}")
        return False

async def upscale_image(image_path, output_path):
    """Upscale an image using fal.ai's RealESRGAN model"""
    fal_client = FalClient()
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        data_uri = f"data:image/jpeg;base64,{encoded_image}"
    
    try:
        # Submit the upscaling request
        handler = await fal_client.submit_async(
            "fal-ai/real-esrgan",
            arguments={
                "image_url": data_uri,
                "scale": 2,
                "model": "RealESRGAN_x4plus",
                "output_format": "png",
                "face": True
            },
        )
        result = await handler.get()
        
        # Download and save the upscaled image
        image_url = result['image_url']
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(await response.read())
                    return True
                else:
                    print(f"Failed to download upscaled image: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"Error during upscaling: {e}")
        return False
