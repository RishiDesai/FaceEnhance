import gradio as gr
import os
import tempfile
import hashlib
import io
import pickle
import pathlib
import sys
from main import process_face
from PIL import Image

PORT = 7860
CACHE_DIR = "./cache"

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def get_image_hash(img):
    """
    Generate a hash of the image content.
    
    Args:
        img: PIL Image
        
    Returns:
        str: Hash of the image
    """
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
    cache_path = os.path.join(CACHE_DIR, f"{combined_hash}.pkl")
    
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
        # Process the face
        process_face(
            input_path=input_path,
            ref_path=ref_path,
            crop=False,
            upscale=False,
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
    # Create the Gradio interface
    with gr.Blocks(title="Face Enhancement Demo") as demo:
        # Add instructions at the top
        gr.Markdown("""
        # Face Enhancement Demo
        ### Instructions
        1. Upload the target image you want to enhance
        2. Upload a high-quality reference face image
        3. Click 'Enhance Face' to start the process

        Processing takes about 60 seconds. Due to the constraints of this demo, face cropping and upscaling are not applied to the reference image.
        """, elem_id="instructions")

        # Add a horizontal line for separation
        gr.Markdown("---")

        # Main interface layout
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

        # Add examples using gr.Examples
        gr.Markdown("## Examples")
        example_inps = [
            ["examples/dany_gpt_1.png", "examples/dany_face.jpg"],
            ["examples/dany_gpt_2.png", "examples/dany_face.jpg"],
            ["examples/tim_gpt_1.png", "examples/tim_face.jpg"],
            ["examples/tim_gpt_2.png", "examples/tim_face.jpg"],
        ]
        gr.Examples(examples=example_inps, inputs=[input_image, ref_image], outputs=output_image)

    # Launch the Gradio app with queue
    demo.queue(max_size=99)
    
    try:
        demo.launch(
            share=True, 
            server_name="0.0.0.0",
            server_port=PORT,
            quiet=True,
            show_error=True,
        )
    except OSError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_gradio_interface() 