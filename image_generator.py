"""
Image Generation Module for AI Influencer Content Generator
Integrates Stable Diffusion for high-quality image generation
"""

import os
import torch
import numpy as np
from PIL import Image
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from transformers import CLIPTextModel, CLIPTokenizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageGenerator:
    """
    Handles image generation using Stable Diffusion models
    """
    
    def __init__(self, model_id="stabilityai/stable-diffusion-3-medium", device=None):
        """
        Initialize the image generator with specified model
        
        Args:
            model_id (str): HuggingFace model ID for Stable Diffusion
            device (str): Device to run inference on ('cuda', 'cpu', etc.)
        """
        self.model_id = model_id
        
        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Initializing ImageGenerator with model {model_id} on {self.device}")
        
        # Model will be loaded on first use to save memory
        self.pipeline = None
        
    def load_model(self):
        """
        Load the Stable Diffusion model
        """
        if self.pipeline is not None:
            return
        
        try:
            logger.info(f"Loading model {self.model_id}...")
            
            # Load pipeline with optimizations
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None  # Disable safety checker for performance
            )
            
            # Use DPM-Solver++ for faster inference
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory optimization if on CUDA
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()
                
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def generate_image(self, prompt, negative_prompt=None, width=512, height=512, 
                      num_inference_steps=30, guidance_scale=7.5, seed=None):
        """
        Generate an image based on the provided prompt
        
        Args:
            prompt (str): Text prompt for image generation
            negative_prompt (str): Text prompt for elements to avoid
            width (int): Output image width
            height (int): Output image height
            num_inference_steps (int): Number of denoising steps
            guidance_scale (float): How closely to follow the prompt
            seed (int): Random seed for reproducibility
            
        Returns:
            PIL.Image: Generated image
        """
        try:
            # Load model if not already loaded
            if self.pipeline is None:
                self.load_model()
                
            # Set seed for reproducibility if provided
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None
                
            # Default negative prompt for better quality if none provided
            if negative_prompt is None:
                negative_prompt = "low quality, blurry, distorted, deformed, disfigured, bad anatomy, watermark"
                
            # Enhanced prompt for better quality
            enhanced_prompt = f"high quality, detailed, professional photograph, {prompt}"
            
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Generate image
            output = self.pipeline(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
            
            # Get image from output
            image = output.images[0]
            
            logger.info("Image generated successfully")
            return image
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    def generate_multiple_images(self, prompt, count=4, **kwargs):
        """
        Generate multiple images with the same prompt
        
        Args:
            prompt (str): Text prompt for image generation
            count (int): Number of images to generate
            **kwargs: Additional arguments for generate_image
            
        Returns:
            list: List of PIL.Image objects
        """
        images = []
        for i in range(count):
            # Use different seeds for variety
            seed = kwargs.get('seed', None)
            if seed is not None:
                kwargs['seed'] = seed + i
                
            logger.info(f"Generating image {i+1}/{count}")
            image = self.generate_image(prompt, **kwargs)
            images.append(image)
            
        return images
    
    def save_image(self, image, output_path):
        """
        Save the generated image to disk
        
        Args:
            image (PIL.Image): Image to save
            output_path (str): Path to save the image
            
        Returns:
            str: Path to the saved image
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save image
            image.save(output_path)
            logger.info(f"Image saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Create generator
    generator = ImageGenerator()
    
    # Generate image
    image = generator.generate_image(
        prompt="professional headshot of a young woman with blonde hair, business attire, neutral background",
        width=512,
        height=512
    )
    
    # Save image
    generator.save_image(image, "output/test_image.png")
