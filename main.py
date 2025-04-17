import argparse
import os
from utils import crop_face, upscale_image

def parse_args():
    parser = argparse.ArgumentParser(description='Face Enhancement Tool')
    parser.add_argument('--input', type=str, required=True, help='Path to the input image')
    parser.add_argument('--ref', type=str, required=True, help='Path to the reference image')
    parser.add_argument('--crop', action='store_true', help='Whether to crop the image')
    parser.add_argument('--upscale', action='store_true', help='Whether to upscale the image')
    parser.add_argument('--output', type=str, required=True, help='Path to save the output image')
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input):
        parser.error(f"Input file does not exist: {args.input}")
    
    # Validate output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        parser.error(f"Output directory does not exist: {output_dir}")
    
    return args

def main():
    args = parse_args()
    print(f"Processing image: {args.input}")
    print(f"Crop enabled: {args.crop}")
    print(f"Upscale enabled: {args.upscale}")
    print(f"Output will be saved to: {args.output}")
    
    face_image = args.ref
    if args.crop:
        crop_face(face_image, "./scratch/cropped_face.png")
        face_image = "./scratch/cropped_face.png"

    if args.upscale:
        upscale_image(face_image, "./scratch/upscaled_face.png")
        face_image = "./scratch/upscaled_face.png"
    

if __name__ == "__main__":
    main() 