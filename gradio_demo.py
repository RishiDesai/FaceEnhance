import gradio as gr
import os
import tempfile
from main import process_face

def enhance_face_gradio(input_image, ref_image):
    """
    Wrapper function for process_face that works with Gradio.
    
    Args:
        input_image: Input image from Gradio
        ref_image: Reference face image from Gradio
        
    Returns:
        str: Path to the enhanced image
    """
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
    
    # Process the face
    process_face(
        input_path=input_path,
        ref_path=ref_path,
        crop=False,
        upscale=False,
        output_path=output_path
    )
    
    # Clean up temporary input and reference files
    os.unlink(input_path)
    os.unlink(ref_path)
    
    return output_path

# Create the Gradio interface
with gr.Blocks(title="Face Enhancement Demo") as demo:
    gr.Markdown("# Face Enhancement Demo")
    gr.Markdown("Upload an input image and a reference face image to enhance the input.")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Input Image", type="pil")
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
    ## Instructions
    1. Upload an image you want to enhance
    2. Upload a reference face image
    3. Click 'Enhance Face' to start the process
    4. Processing takes about 60 seconds
    """)

# Launch the Gradio app with queue
if __name__ == "__main__":
    # Set up queue with max_size=20 and concurrency=1
    demo.queue(max_size=20)  # Configure queue size
    demo.launch(
        share=False,  # Set to True if you want a public link
        server_name="0.0.0.0",  # Make available on all network interfaces
        server_port=7860,  # Default Gradio port
        # concurrency_count=1  # Process one job at a time
    ) 