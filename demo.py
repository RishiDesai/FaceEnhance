import os
from install import install

if "HF_DEMO" in os.environ:
    # Global variable to track if install() has been run; only for deploying on HF space
    INSTALLED = False
    if not INSTALLED:
        install(is_hf_space=True, cache_models=True)
        INSTALLED = True

import gradio as gr
import tempfile
import hashlib
import io
import pickle
import sys
from test import process_face
from PIL import Image

INPUT_CACHE_DIR = "./cache"
os.makedirs(INPUT_CACHE_DIR, exist_ok=True)

def get_image_hash(img):
    """Generate a hash of the image content."""
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return hashlib.md5(img_bytes.getvalue()).hexdigest()

def enhance_face_gradio(input_image, ref_image):
    """
    Wrapper function for process_face that works with Gradio.
    
    Args:
        input_image: Input image from Gradio
        ref_image: Reference face image from Gradio
        
    Returns:
        PIL Image: Enhanced image
    """
    # Generate hashes for both images
    input_hash = get_image_hash(input_image)
    ref_hash = get_image_hash(ref_image)
    combined_hash = f"{input_hash}_{ref_hash}"
    cache_path = os.path.join(INPUT_CACHE_DIR, f"{combined_hash}.pkl")
    
    # Check if result exists in cache
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                result_img = pickle.load(f)
                print(f"Returning cached result for images with hash {combined_hash}")
                return result_img
        except (pickle.PickleError, IOError) as e:
            print(f"Error loading from cache: {e}")
            # Continue to processing if cache load fails
    
    # Create temporary files for input, reference, and output
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as input_file, \
         tempfile.NamedTemporaryFile(suffix=".png", delete=False) as ref_file, \
         tempfile.NamedTemporaryFile(suffix=".png", delete=False) as output_file:
        
        input_path = input_file.name
        ref_path = ref_file.name
        output_path = output_file.name
    
    # Save uploaded images to temporary files
    input_image.save(input_path)
    ref_image.save(ref_path)
    
    try:
        process_face(
            input_path=input_path,
            ref_path=ref_path,
            output_path=output_path
        )
    except Exception as e:
        # Handle the error, log it, and return an error message
        print(f"Error processing face: {e}")
        return "An error occurred while processing the face. Please try again."
    finally:
        # Clean up temporary input and reference files
        os.unlink(input_path)
        os.unlink(ref_path)
    
    # Load the output image
    result_img = Image.open(output_path)
    
    # Cache the result
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(result_img, f)
            print(f"Cached result for images with hash {combined_hash}")
    except (pickle.PickleError, IOError) as e:
        print(f"Error caching result: {e}")
    
    return result_img

def create_gradio_interface():
    with gr.Blocks(title="Face Enhancement") as demo:
        gr.Markdown("""
        # Face Enhance
        ### Instructions
        1. Upload the target image you want to enhance
        2. Upload a high-quality face image
        3. Click 'Enhance Face'

        Processing takes around 30 seconds.
        """, elem_id="instructions")

        gr.Markdown("---")

        with gr.Row():
            with gr.Column():
                input_image = gr.Image(label="Target Image", type="pil")
                ref_image = gr.Image(label="Reference Face", type="pil")
                enhance_button = gr.Button("Enhance Face")
            
            with gr.Column():
                output_image = gr.Image(label="Enhanced Result")
        
        enhance_button.click(
            fn=enhance_face_gradio,
            inputs=[input_image, ref_image],
            outputs=output_image,
            queue=True  # Enable queue for sequential processing
        )
        gr.Markdown("""
        ## Examples
        Click on an example to load the images into the interface.
        """)
        example_inps = [
            ["examples/dany_gpt_1.png", "examples/dany_face.jpg"],
            ["examples/dany_gpt_2.png", "examples/dany_face.jpg"],
            ["examples/tim_gpt_1.png", "examples/tim_face.jpg"],
            ["examples/tim_gpt_2.png", "examples/tim_face.jpg"],
            ["examples/elon_gpt.png", "examples/elon_face.png"],
        ]
        gr.Examples(examples=example_inps, inputs=[input_image, ref_image], outputs=output_image)

        gr.Markdown("""
        ## Notes
        Check out the code [here](https://github.com/RishiDesai/FaceEnhance) and see my [blog post](https://rishidesai.github.io/posts/face-enhancement-techniques/) for more information.
        
        Due to the constraints of this demo, face cropping and upscaling are not applied to the reference image.
        """)

    # Launch the Gradio app with queue
    demo.queue(max_size=99)
    
    try:
        demo.launch()
    except OSError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_gradio_interface() 