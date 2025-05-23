import argparse
import os
import shutil
from face_enhance import face_enhance

def parse_args():
    parser = argparse.ArgumentParser(description='Face Enhancement Tool')
    parser.add_argument('--input', type=str, required=True, help='Path to the input image')
    parser.add_argument('--ref', type=str, required=True, help='Path to the reference image')
    parser.add_argument('--output', type=str, required=True, help='Path to save the output image')
    parser.add_argument('--id_weight', type=float, default=0.75, help='face ID weight')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        parser.error(f"Input file does not exist: {args.input}")
    if not os.path.exists(args.ref):
        parser.error(f"Reference file does not exist: {args.ref}")
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        parser.error(f"Output directory does not exist: {output_dir}")
    return args

def create_scratch_dir():
    """Create a new numbered directory in ./ComfyUI/input/scratch"""
    base_dir = "./ComfyUI/input/scratch"

    # Create base directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)

    # Get existing directories and find the next number
    existing_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.isdigit()]
    next_dir_num = 1
    if existing_dirs:
        next_dir_num = max([int(d) for d in existing_dirs]) + 1

    # Create the new directory
    new_dir = os.path.join(base_dir, str(next_dir_num))
    os.makedirs(new_dir, exist_ok=True)

    return new_dir

def process_face(input_path, ref_path, output_path=None, id_weight=0.75):
    """
    Process a face image using the given parameters.

    Returns:
        str: Path to the scratch directory used for processing
    """
    print(f"Processing image: {input_path}")
    print(f"Reference image: {ref_path}")
    print(f"Output will be saved to: {output_path}")

    # Create a new scratch directory for this run
    scratch_dir = create_scratch_dir()
    print(f"Created scratch directory: {scratch_dir}")

    # Copy input and reference images to scratch directory
    input_filename = os.path.basename(input_path)
    ref_filename = os.path.basename(ref_path)

    scratch_input = os.path.join(scratch_dir, input_filename)
    scratch_ref = os.path.join(scratch_dir, ref_filename)

    shutil.copy(input_path, scratch_input)
    shutil.copy(ref_path, scratch_ref)

    # Convert paths to ComfyUI format (relative to ComfyUI/input/)
    # For example: "./ComfyUI/input/scratch/1/image.png" becomes "scratch/1/image.png"
    comfy_ref_path = os.path.relpath(scratch_ref, "./ComfyUI/input")
    comfy_input_path = os.path.relpath(scratch_input, "./ComfyUI/input")

    face_enhance(comfy_ref_path, comfy_input_path, output_path, dist_image=f"{output_path}_dist.png", id_weight=id_weight)

    print(f"Enhanced image saved to: {output_path}")
    print(f"Working files are in: {scratch_dir}")

    return scratch_dir

def main():
    args = parse_args()
    return process_face(
        input_path=args.input,
        ref_path=args.ref,
        output_path=args.output,
        id_weight=args.id_weight
    )

if __name__ == "__main__":
    main()