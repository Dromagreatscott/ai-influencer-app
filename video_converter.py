"""
Image to Video Conversion Module for AI Influencer Content Generator
Integrates open-source tools for converting static images to videos
"""

import os
import cv2
import numpy as np
from PIL import Image
import tempfile
import subprocess
import logging
import uuid
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageToVideoConverter:
    """
    Handles conversion of static images to videos with motion
    """
    
    def __init__(self, output_dir="videos"):
        """
        Initialize the image to video converter
        
        Args:
            output_dir (str): Directory to store output videos
        """
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized ImageToVideoConverter with output at {output_dir}")
        
    def animate_image(self, image_path, duration=5, motion_type="subtle", fps=30):
        """
        Animate a static image with motion effects
        
        Args:
            image_path (str): Path to the input image
            duration (int): Duration of output video in seconds
            motion_type (str): Type of motion effect ("subtle", "medium", "strong")
            fps (int): Frames per second for output video
            
        Returns:
            str: Path to the output video file
        """
        try:
            # Load image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Could not load image from {image_path}")
            elif isinstance(image_path, Image.Image):
                image = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
            else:
                raise ValueError("Image must be a PIL Image or valid file path")
                
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate frames with motion effect
                total_frames = duration * fps
                logger.info(f"Generating {total_frames} frames with {motion_type} motion")
                
                for i in range(total_frames):
                    # Calculate progress percentage
                    progress = i / total_frames
                    
                    # Apply motion effect based on type
                    if motion_type == "subtle":
                        # Subtle zoom and pan
                        zoom_factor = 1.0 + 0.05 * np.sin(progress * np.pi)
                        pan_x = int(width * 0.02 * np.sin(progress * 2 * np.pi))
                        pan_y = int(height * 0.02 * np.cos(progress * 2 * np.pi))
                    elif motion_type == "medium":
                        # Medium zoom and pan
                        zoom_factor = 1.0 + 0.1 * np.sin(progress * np.pi)
                        pan_x = int(width * 0.05 * np.sin(progress * 2 * np.pi))
                        pan_y = int(height * 0.05 * np.cos(progress * 2 * np.pi))
                    elif motion_type == "strong":
                        # Strong zoom and pan
                        zoom_factor = 1.0 + 0.15 * np.sin(progress * np.pi)
                        pan_x = int(width * 0.1 * np.sin(progress * 2 * np.pi))
                        pan_y = int(height * 0.1 * np.cos(progress * 2 * np.pi))
                    else:
                        raise ValueError(f"Unknown motion type: {motion_type}")
                    
                    # Apply zoom
                    zoomed_width = int(width / zoom_factor)
                    zoomed_height = int(height / zoom_factor)
                    
                    # Calculate crop region
                    x1 = (width - zoomed_width) // 2 + pan_x
                    y1 = (height - zoomed_height) // 2 + pan_y
                    x2 = x1 + zoomed_width
                    y2 = y1 + zoomed_height
                    
                    # Ensure crop region is within image bounds
                    x1 = max(0, min(x1, width - zoomed_width))
                    y1 = max(0, min(y1, height - zoomed_height))
                    x2 = min(width, max(x2, zoomed_width))
                    y2 = min(height, max(y2, zoomed_height))
                    
                    # Crop and resize
                    cropped = image[y1:y2, x1:x2]
                    frame = cv2.resize(cropped, (width, height))
                    
                    # Save frame
                    frame_path = os.path.join(temp_dir, f"frame_{i:04d}.jpg")
                    cv2.imwrite(frame_path, frame)
                
                # Generate unique output filename
                output_filename = f"video_{uuid.uuid4()}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Use ffmpeg to create video from frames
                logger.info(f"Creating video from {total_frames} frames")
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file if it exists
                    "-framerate", str(fps),
                    "-i", os.path.join(temp_dir, "frame_%04d.jpg"),
                    "-c:v", "libx264",
                    "-profile:v", "high",
                    "-crf", "18",  # High quality
                    "-pix_fmt", "yuv420p",
                    output_path
                ]
                
                # Run ffmpeg
                subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                logger.info(f"Video created successfully at {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error animating image: {str(e)}")
            raise
    
    def face_swap_video(self, face_image_path, target_video_path):
        """
        Placeholder for face swap functionality
        In the MVP, this will be a simplified implementation
        
        Args:
            face_image_path (str): Path to the face image
            target_video_path (str): Path to the target video
            
        Returns:
            str: Path to the output video file
        """
        try:
            logger.info(f"Face swap requested for {face_image_path} onto {target_video_path}")
            
            # For MVP, we'll create a placeholder implementation
            # that simply adds a watermark to the video
            
            # Generate unique output filename
            output_filename = f"faceswap_{uuid.uuid4()}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract frames from target video
                extract_cmd = [
                    "ffmpeg",
                    "-i", target_video_path,
                    "-vf", "fps=30",
                    os.path.join(temp_dir, "frame_%04d.jpg")
                ]
                subprocess.run(extract_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Load face image as watermark
                face_img = cv2.imread(face_image_path)
                if face_img is None:
                    raise ValueError(f"Could not load face image from {face_image_path}")
                
                # Resize face image to small watermark
                face_img = cv2.resize(face_img, (100, 100))
                
                # Process each frame
                frames = sorted(os.listdir(temp_dir))
                for frame_file in frames:
                    if not frame_file.endswith('.jpg'):
                        continue
                        
                    frame_path = os.path.join(temp_dir, frame_file)
                    frame = cv2.imread(frame_path)
                    
                    # Add face image as watermark
                    h, w = frame.shape[:2]
                    fh, fw = face_img.shape[:2]
                    frame[h-fh-10:h-10, w-fw-10:w-10] = face_img
                    
                    # Save modified frame
                    cv2.imwrite(frame_path, frame)
                
                # Create video from modified frames
                create_cmd = [
                    "ffmpeg",
                    "-y",
                    "-framerate", "30",
                    "-i", os.path.join(temp_dir, "frame_%04d.jpg"),
                    "-c:v", "libx264",
                    "-profile:v", "high",
                    "-crf", "18",
                    "-pix_fmt", "yuv420p",
                    output_path
                ]
                subprocess.run(create_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                logger.info(f"Face swap video created at {output_path}")
                logger.warning("Note: This is a placeholder implementation for the MVP")
                return output_path
                
        except Exception as e:
            logger.error(f"Error in face swap: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Create converter
    converter = ImageToVideoConverter()
    
    # Animate image
    video_path = converter.animate_image(
        "test_image.jpg",
        duration=5,
        motion_type="medium"
    )
    
    print(f"Video created at: {video_path}")
