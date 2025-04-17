#!/usr/bin/env python
import argparse
from pathlib import Path
from PIL import Image
import numpy as np

def create_comparison_gif(before_img_path, after_img_path, output_path=None, duration=100, frames=20):
    """
    Create a comparison GIF with a vertical bar revealing the 'after' image.
    
    Args:
        before_img_path (str): Path to the 'before' image
        after_img_path (str): Path to the 'after' image
        output_path (str, optional): Path for the output GIF. Defaults to 'comparison.gif'
        duration (int, optional): Duration of each frame in ms. Defaults to 100.
        frames (int, optional): Number of frames in the GIF. Defaults to 20.
    
    Returns:
        str: Path to the created GIF
    """
    # Default output path
    if output_path is None:
        output_path = 'comparison.gif'
    
    # Open images and ensure they have the same size
    before_img = Image.open(before_img_path)
    after_img = Image.open(after_img_path)
    
    # Resize if they're different
    if before_img.size != after_img.size:
        after_img = after_img.resize(before_img.size, Image.LANCZOS)
    
    width, height = before_img.size
    
    # Create frames for the GIF
    gif_frames = []
    
    for i in range(frames + 1):
        # Calculate position of the reveal bar
        bar_position = int((width * i) / frames)
        
        # Create a new frame
        frame = Image.new('RGBA', (width, height))
        
        # Paste the 'before' image
        frame.paste(before_img, (0, 0))
        
        # Create a mask for the 'after' image
        mask = Image.new('L', (width, height), 0)
        mask_array = np.array(mask)
        mask_array[:, :bar_position] = 255
        mask = Image.fromarray(mask_array)
        
        # Paste the 'after' image with the mask
        frame.paste(after_img, (0, 0), mask)
        
        # Add to frames
        gif_frames.append(frame.convert('RGBA'))
    
    # Save as GIF
    gif_frames[0].save(
        output_path,
        save_all=True,
        append_images=gif_frames[1:],
        optimize=False,
        duration=duration,
        loop=0,
        disposal=2
    )
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Create a before/after comparison GIF with a sliding reveal effect')
    parser.add_argument('before_image', help='Path to the before image')
    parser.add_argument('after_image', help='Path to the after image')
    parser.add_argument('--output', '-o', help='Output path for the GIF', default='comparison.gif')
    parser.add_argument('--duration', '-d', type=int, help='Duration of each frame in ms', default=100)
    parser.add_argument('--frames', '-f', type=int, help='Number of frames to generate', default=20)
    
    args = parser.parse_args()
    
    output_path = create_comparison_gif(
        args.before_image,
        args.after_image,
        args.output,
        args.duration,
        args.frames
    )
    
    print(f"Created comparison GIF: {output_path}")

if __name__ == "__main__":
    main() 