"""
Integration utilities for AI Influencer Content Generator
Provides helper functions for connecting different modules
"""

import os
import logging
from PIL import Image
import json
import time
import uuid

# Import core modules
from models.image_generator import ImageGenerator
from models.persona_manager import PersonaManager
from models.video_converter import ImageToVideoConverter
from models.content_manager import ContentManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationManager:
    """
    Manages integration between different modules
    """
    
    def __init__(self, base_dir="/home/ubuntu/ai_influencer_app"):
        """
        Initialize the integration manager
        
        Args:
            base_dir (str): Base directory for the application
        """
        self.base_dir = base_dir
        
        # Create data directories
        self.data_dir = os.path.join(base_dir, "data")
        self.personas_dir = os.path.join(self.data_dir, "personas")
        self.content_dir = os.path.join(self.data_dir, "content")
        self.uploads_dir = os.path.join(self.data_dir, "uploads")
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.personas_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        # Initialize core modules
        self.image_generator = ImageGenerator()
        self.persona_manager = PersonaManager(storage_dir=self.personas_dir)
        self.video_converter = ImageToVideoConverter(output_dir=os.path.join(self.content_dir, "videos"))
        self.content_manager = ContentManager(storage_dir=self.content_dir)
        
        logger.info(f"Initialized IntegrationManager with base directory {base_dir}")
    
    def create_persona_workflow(self, name, reference_image=None, description=None, attributes=None):
        """
        Execute the complete persona creation workflow
        
        Args:
            name (str): Name of the persona
            reference_image (str or PIL.Image): Reference image or path
            description (str): Text description of the persona
            attributes (dict): Additional attributes for the persona
            
        Returns:
            dict: Persona data with preview images
        """
        try:
            logger.info(f"Starting persona creation workflow for {name}")
            
            # Step 1: Create basic persona
            persona = self.persona_manager.create_persona(
                name=name,
                reference_image=reference_image,
                description=description,
                attributes=attributes
            )
            
            # Step 2: Extract identity features
            persona = self.persona_manager.extract_identity_features(persona["id"])
            
            # Step 3: Generate preview images
            preview_images = []
            
            # Generate different preview styles
            styles = ["professional headshot", "casual portrait", "full body shot"]
            
            for style in styles:
                # Construct prompt based on persona attributes
                age_range = attributes.get("age_range", "25-35")
                gender = attributes.get("gender", "person")
                
                prompt = f"{style} of a {age_range} year old {gender}, "
                
                if "style" in attributes:
                    prompt += f"{attributes['style']} style, "
                    
                if description:
                    prompt += f"{description}, "
                    
                prompt += "high quality, professional photography, studio lighting"
                
                # Generate image
                image = self.image_generator.generate_image(
                    prompt=prompt,
                    width=512,
                    height=512,
                    num_inference_steps=30,
                    guidance_scale=7.5
                )
                
                # Save image to content store
                content_data = self.content_manager.save_image(
                    image=image,
                    persona_id=persona["id"],
                    metadata={
                        "prompt": prompt,
                        "style": style,
                        "is_preview": True
                    }
                )
                
                preview_images.append(content_data)
            
            # Update persona with preview images
            self.persona_manager.update_persona(
                persona["id"],
                {"preview_images": [img["id"] for img in preview_images]}
            )
            
            # Get updated persona data
            persona = self.persona_manager.get_persona(persona["id"])
            
            logger.info(f"Completed persona creation workflow for {name}")
            return persona
            
        except Exception as e:
            logger.error(f"Error in persona creation workflow: {str(e)}")
            raise
    
    def generate_content_workflow(self, persona_id, content_type, settings=None, count=1):
        """
        Execute the content generation workflow
        
        Args:
            persona_id (str): ID of the persona
            content_type (str): Type of content to generate
            settings (dict): Generation settings
            count (int): Number of items to generate
            
        Returns:
            list: Generated content data
        """
        try:
            logger.info(f"Starting content generation workflow for persona {persona_id}")
            
            # Get persona data
            persona = self.persona_manager.get_persona(persona_id)
            if not persona:
                raise ValueError(f"Persona with ID {persona_id} not found")
            
            # Initialize settings if not provided
            if settings is None:
                settings = {}
            
            # Initialize results list
            results = []
            
            # Process based on content type
            if content_type == "portrait":
                results = self._generate_portrait_images(persona, settings, count)
            elif content_type == "full_body":
                results = self._generate_full_body_images(persona, settings, count)
            elif content_type == "action":
                results = self._generate_action_images(persona, settings, count)
            elif content_type == "social_post":
                results = self._generate_social_post_images(persona, settings, count)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
            
            logger.info(f"Completed content generation workflow, created {len(results)} items")
            return results
            
        except Exception as e:
            logger.error(f"Error in content generation workflow: {str(e)}")
            raise
    
    def create_video_workflow(self, image_id=None, video_type="animate", settings=None):
        """
        Execute the video creation workflow
        
        Args:
            image_id (str): ID of the source image
            video_type (str): Type of video to create
            settings (dict): Video creation settings
            
        Returns:
            dict: Video content data
        """
        try:
            logger.info(f"Starting video creation workflow for image {image_id}")
            
            # Initialize settings if not provided
            if settings is None:
                settings = {}
            
            # Get image content data
            image_content = self.content_manager.get_content(image_id)
            if not image_content:
                raise ValueError(f"Image content with ID {image_id} not found")
            
            # Get persona ID from image content
            persona_id = image_content.get("persona_id")
            
            # Process based on video type
            if video_type == "animate":
                # Get motion type from settings
                motion_type = settings.get("motion_type", "subtle")
                duration = settings.get("duration", 5)
                
                # Animate image
                video_path = self.video_converter.animate_image(
                    image_path=image_content["file_path"],
                    duration=duration,
                    motion_type=motion_type,
                    fps=30
                )
                
                # Save video to content store
                video_content = self.content_manager.save_video(
                    video_path=video_path,
                    persona_id=persona_id,
                    metadata={
                        "source_image_id": image_id,
                        "video_type": video_type,
                        "settings": settings
                    }
                )
                
                logger.info(f"Created animated video {video_content['id']} from image {image_id}")
                return video_content
                
            elif video_type == "face_swap":
                # Get target video path from settings
                target_video = settings.get("target_video")
                if not target_video:
                    raise ValueError("Target video is required for face swap")
                
                # Perform face swap
                video_path = self.video_converter.face_swap_video(
                    face_image_path=image_content["file_path"],
                    target_video_path=target_video
                )
                
                # Save video to content store
                video_content = self.content_manager.save_video(
                    video_path=video_path,
                    persona_id=persona_id,
                    metadata={
                        "source_image_id": image_id,
                        "video_type": video_type,
                        "target_video": target_video,
                        "settings": settings
                    }
                )
                
                logger.info(f"Created face swap video {video_content['id']} from image {image_id}")
                return video_content
                
            else:
                raise ValueError(f"Unknown video type: {video_type}")
            
        except Exception as e:
            logger.error(f"Error in video creation workflow: {str(e)}")
            raise
    
    def export_workflow(self, content_ids, export_format="original", platform=None):
        """
        Execute the export workflow
        
        Args:
            content_ids (list): List of content IDs to export
            export_format (str): Format for export
            platform (str): Platform optimization
            
        Returns:
            str: Path to export zip file
        """
        try:
            logger.info(f"Starting export workflow for {len(content_ids)} content items")
            
            # Export content
            export_path = self.content_manager.export_content(
                content_ids=content_ids,
                export_format=export_format,
                platform=platform
            )
            
            logger.info(f"Completed export workflow, created {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error in export workflow: {str(e)}")
            raise
    
    def _generate_portrait_images(self, persona, settings, count):
        """
        Generate portrait images for a persona
        
        Args:
            persona (dict): Persona data
            settings (dict): Generation settings
            count (int): Number of images to generate
            
        Returns:
            list: Generated content data
        """
        # Extract settings
        style = settings.get("style", "professional")
        setting = settings.get("setting", "studio")
        additional_prompt = settings.get("additional_prompt", "")
        
        # Construct base prompt
        name = persona.get("name", "person")
        attributes = persona.get("attributes", {})
        age_range = attributes.get("age_range", "25-35")
        gender = attributes.get("gender", "person")
        
        base_prompt = f"professional portrait of {name}, a {age_range} year old {gender}, "
        
        # Add style
        if style == "professional":
            base_prompt += "business attire, professional headshot, "
        elif style == "casual":
            base_prompt += "casual attire, relaxed pose, "
        elif style == "artistic":
            base_prompt += "artistic portrait, creative lighting, "
        elif style == "glamorous":
            base_prompt += "glamorous style, fashion photography, "
        
        # Add setting
        if setting == "studio":
            base_prompt += "studio background, professional lighting, "
        elif setting == "outdoor":
            base_prompt += "outdoor setting, natural lighting, "
        elif setting == "urban":
            base_prompt += "urban environment, city background, "
        elif setting == "nature":
            base_prompt += "nature background, scenic environment, "
        
        # Add quality indicators
        base_prompt += "high quality, detailed, professional photography, "
        
        # Add additional prompt if provided
        if additional_prompt:
            base_prompt += f"{additional_prompt}, "
        
        # Generate images
        images = self.image_generator.generate_multiple_images(
            prompt=base_prompt,
            count=count,
            width=settings.get("width", 512),
            height=settings.get("height", 512),
            num_inference_steps=settings.get("steps", 30),
            guidance_scale=settings.get("guidance", 7.5)
        )
        
        # Save images to content store
        content_items = []
        for i, image in enumerate(images):
            content_data = self.content_manager.save_image(
                image=image,
                persona_id=persona["id"],
                metadata={
                    "prompt": base_prompt,
                    "content_type": "portrait",
                    "style": style,
                    "setting": setting,
                    "settings": settings
                }
            )
            content_items.append(content_data)
        
        return content_items
    
    def _generate_full_body_images(self, persona, settings, count):
        """
        Generate full body images for a persona
        
        Args:
            persona (dict): Persona data
            settings (dict): Generation settings
            count (int): Number of images to generate
            
        Returns:
            list: Generated content data
        """
        # Similar implementation to _generate_portrait_images
        # but with full body prompts
        
        # Extract settings
        style = settings.get("style", "professional")
        setting = settings.get("setting", "studio")
        additional_prompt = settings.get("additional_prompt", "")
        
        # Construct base prompt
        name = persona.get("name", "person")
        attributes = persona.get("attributes", {})
        age_range = attributes.get("age_range", "25-35")
        gender = attributes.get("gender", "person")
        
        base_prompt = f"full body shot of {name}, a {age_range} year old {gender}, "
        
        # Add style and setting similar to portrait function
        # ...
        
        # For MVP, we'll use a simplified implementation
        if style == "professional":
            base_prompt += "business attire, professional pose, "
        elif style == "casual":
            base_prompt += "casual attire, relaxed pose, "
        
        if setting == "studio":
            base_prompt += "studio background, professional lighting, "
        elif setting == "outdoor":
            base_prompt += "outdoor setting, natural lighting, "
        
        # Add quality indicators
        base_prompt += "high quality, detailed, professional photography, full body visible, "
        
        # Add additional prompt if provided
        if additional_prompt:
            base_prompt += f"{additional_prompt}, "
        
        # Generate and save images (same as portrait function)
        # ...
        
        # Generate images
        images = self.image_generator.generate_multiple_images(
            prompt=base_prompt,
            count=count,
            width=settings.get("width", 512),
            height=settings.get("height", 768),  # Taller for full body
            num_inference_steps=settings.get("steps", 30),
            guidance_scale=settings.get("guidance", 7.5)
        )
        
        # Save images to content store
        content_items = []
        for i, image in enumerate(images):
            content_data = self.content_manager.save_image(
                image=image,
                persona_id=persona["id"],
                metadata={
                    "prompt": base_prompt,
                    "content_type": "full_body",
                    "style": style,
                    "setting": setting,
                    "settings": settings
                }
            )
            content_items.append(content_data)
        
        return content_items
    
    def _generate_action_images(self, persona, settings, count):
        """
        Generate action images for a persona
        
        Args:
            persona (dict): Persona data
            settings (dict): Generation settings
            count (int): Number of images to generate
            
        Returns:
            list: Generated content data
        """
        # Extract settings
        action = settings.get("action", "working")
        setting = settings.get("setting", "office")
        additional_prompt = settings.get("additional_prompt", "")
        
        # Construct base prompt
        name = persona.get("name", "person")
        attributes = persona.get("attributes", {})
        age_range = attributes.get("age_range", "25-35")
        gender = attributes.get("gender", "person")
        
        base_prompt = f"{name}, a {age_range} year old {gender}, "
        
        # Add action
        if action == "working":
            base_prompt += "working on computer, focused expression, "
        elif action == "presenting":
            base_prompt += "giving a presentation, confident pose, "
        elif action == "meeting":
            base_prompt += "in a business meeting, engaged expression, "
        elif action == "exercising":
            base_prompt += "exercising, athletic pose, "
        
        # Add setting
        if setting == "office":
            base_prompt += "in an office environment, professional setting, "
        elif setting == "conference":
            base_prompt += "in a conference room, business environment, "
        elif setting == "outdoor":
            base_prompt += "in an outdoor setting, "
        elif setting == "gym":
            base_prompt += "in a gym, fitness environment, "
        
        # Add quality indicators
        base_prompt += "high quality, detailed, professional photography, "
        
        # Add additional prompt if provided
        if additional_prompt:
            base_prompt += f"{additional_prompt}, "
        
        # Generate images
        images = self.image_generator.generate_multiple_images(
            prompt=base_prompt,
            count=count,
            width=settings.get("width", 512),
            height=settings.get("height", 512),
            num_inference_steps=settings.get("steps", 30),
            guidance_scale=settings.get("guidance", 7.5)
        )
        
        # Save images to content store
        content_items = []
        for i, image in enumerate(images):
            content_data = self.content_manager.save_image(
                image=image,
                persona_id=persona["id"],
                metadata={
                    "prompt": base_prompt,
                    "content_type": "action",
                    "action": action,
                    "setting": setting,
                    "settings": settings
                }
            )
            content_items.append(content_data)
        
        return content_items
    
    def _generate_social_post_images(self, persona, settings, count):
        """
        Generate social media post images for a persona
        
        Args:
            persona (dict): Persona data
            settings (dict): Generation settings
            count (int): Number of images to generate
            
        Returns:
            list: Generated content data
        """
        # Extract settings
        platform = settings.get("platform", "instagram")
        theme = settings.get("theme", "professional")
        additional_prompt = settings.get("additional_prompt", "")
        
        # Construct base prompt
        name = persona.get("name", "person")
        attributes = persona.get("attributes", {})
        age_range = attributes.get("age_range", "25-35")
        gender = attributes.get("gender", "person")
        
        base_prompt = f"social media post featuring {name}, a {age_range} year old {gender}, "
        
        # Add platform-specific elements
        if platform == "instagram":
            base_prompt += "instagram style post, square format, "
        elif platform == "linkedin":
            base_prompt += "linkedin professional post, business context, "
        elif platform == "twitter":
            base_prompt += "twitter post image, engaging content, "
        
        # Add theme
        if theme == "professional":
            base_prompt += "professional context, business theme, "
        elif theme == "lifestyle":
            base_prompt += "lifestyle content, aspirational setting, "
        elif theme == "travel":
            base_prompt += "travel content, scenic location, "
        elif theme == "fitness":
            base_prompt += "fitness content, active lifestyle, "
        
        # Add quality indicators
        base_prompt += "high quality, detailed, professional photography, social media aesthetic, "
        
        # Add additional prompt if provided
        if additional_prompt:
            base_prompt += f"{additional_prompt}, "
        
        # Generate images
        images = self.image_generator.generate_multiple_images(
            prompt=base_prompt,
            count=count,
            width=settings.get("width", 1024),
            height=settings.get("height", 1024),
            num_inference_steps=settings.get("steps", 30),
            guidance_scale=settings.get("guidance", 7.5)
        )
        
        # Save images to content store
        content_items = []
        for i, image in enumerate(images):
            content_data = self.content_manager.save_image(
                image=image,
                persona_id=persona["id"],
                metadata={
                    "prompt": base_prompt,
                    "content_type": "social_post",
                    "platform": platform,
                    "theme": theme,
                    "settings": settings
                }
            )
            content_items.append(content_data)
        
        return content_items

# Example usage
if __name__ == "__main__":
    # Create integration manager
    manager = IntegrationManager()
    
    # Create test persona
    persona = manager.create_persona_workflow(
        name="Test Persona",
        description="A professional business person with a confident demeanor",
        attributes={
            "age_range": "30-40",
            "gender": "person",
            "style": "Professional"
        }
    )
    
    print(f"Created persona: {persona['name']} ({persona['id']})")
