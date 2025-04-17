import gradio as gr
import os
import tempfile
# from main import process_face
from PIL import Image

def enhance_face_gradio(input_image, ref_image):
    """
    Wrapper function for process_face that works with Gradio.
    
    Args:
        input_image: Input image from Gradio
        ref_image: Reference face image from Gradio
        
    Returns:
        PIL Image: Enhanced image
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
    
    try:
        # Process the face
        # process_face(
        #     input_path=input_path,
        #     ref_path=ref_path,
        #     crop=False,
        #     upscale=False,
        #     output_path=output_path
        # )
        pass
    except Exception as e:
        # Handle the error, log it, and return an error message
        print(f"Error processing face: {e}")
        return "An error occurred while processing the face. Please try again."

    finally:
        # Clean up temporary input and reference files
        os.unlink(input_path)
        os.unlink(ref_path)
    
    return Image.open(output_path)

def create_gradio_interface():
    # Create the Gradio interface
    with gr.Blocks(title="Face Enhancement Demo") as demo:
        # Add instructions at the top
        gr.Markdown("""
        # Face Enhancement Demo
        ### Instructions
        1. Upload an image you want to enhance
        2. Upload a reference face image
        3. Click 'Enhance Face' to start the process
        4. Processing takes about 60 seconds
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

        # Add examples at the bottom in a table format
        with gr.Row():
            gr.Markdown("### Examples")
            with gr.Column():
                gr.Image("examples/chatgpt_dany_1.png", label="Target Image Example")
                gr.Image("examples/dany_face.jpg", label="Reference Face Example")

    # Launch the Gradio app with queue
    demo.queue(max_size=20)  # Configure queue size
    demo.launch(
        share=False,  # Set to True if you want a public link
        server_name="0.0.0.0",  # Make available on all network interfaces
        server_port=7860,  # Default Gradio port
    )


if __name__ == "__main__":
    create_gradio_interface() 