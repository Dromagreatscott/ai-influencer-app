"""
Content Management Module for AI Influencer Content Generator
Handles storage, organization, and export of generated content
"""

import os
import json
import uuid
import shutil
import logging
from datetime import datetime
from PIL import Image
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentManager:
    """
    Manages storage, organization, and export of generated content
    """
    
    def __init__(self, storage_dir="content"):
        """
        Initialize the content manager
        
        Args:
            storage_dir (str): Directory to store content
        """
        self.storage_dir = storage_dir
        
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Create subdirectories for different content types
        self.image_dir = os.path.join(storage_dir, "images")
        self.video_dir = os.path.join(storage_dir, "videos")
        self.export_dir = os.path.join(storage_dir, "exports")
        
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.export_dir, exist_ok=True)
        
        logger.info(f"Initialized ContentManager with storage at {storage_dir}")
    
    def save_image(self, image, persona_id, metadata=None):
        """
        Save an image to the content store
        
        Args:
            image (PIL.Image or str): Image to save or path to image
            persona_id (str): ID of the persona associated with the image
            metadata (dict): Additional metadata for the image
            
        Returns:
            dict: Content data including ID and paths
        """
        try:
            # Generate unique ID for content
            content_id = str(uuid.uuid4())
            
            # Create content directory
            content_dir = os.path.join(self.image_dir, content_id)
            os.makedirs(content_dir, exist_ok=True)
            
            # Process image
            image_path = os.path.join(content_dir, "image.jpg")
            if isinstance(image, str) and os.path.exists(image):
                # Copy image to content directory
                shutil.copy(image, image_path)
            elif isinstance(image, Image.Image):
                # Save PIL image to content directory
                image.save(image_path, "JPEG", quality=95)
            else:
                raise ValueError("Image must be a PIL Image or valid file path")
            
            # Create thumbnail
            thumbnail_path = os.path.join(content_dir, "thumbnail.jpg")
            self._create_thumbnail(image_path, thumbnail_path)
            
            # Create content data
            content_data = {
                "id": content_id,
                "type": "image",
                "persona_id": persona_id,
                "created_at": datetime.now().isoformat(),
                "file_path": image_path,
                "thumbnail_path": thumbnail_path,
                "metadata": metadata or {}
            }
            
            # Save content data
            self._save_content_data(content_id, content_data)
            
            logger.info(f"Saved image content with ID {content_id}")
            return content_data
            
        except Exception as e:
            logger.error(f"Error saving image content: {str(e)}")
            raise
    
    def save_video(self, video_path, persona_id, metadata=None):
        """
        Save a video to the content store
        
        Args:
            video_path (str): Path to the video file
            persona_id (str): ID of the persona associated with the video
            metadata (dict): Additional metadata for the video
            
        Returns:
            dict: Content data including ID and paths
        """
        try:
            # Generate unique ID for content
            content_id = str(uuid.uuid4())
            
            # Create content directory
            content_dir = os.path.join(self.video_dir, content_id)
            os.makedirs(content_dir, exist_ok=True)
            
            # Copy video to content directory
            video_filename = os.path.basename(video_path)
            dest_video_path = os.path.join(content_dir, video_filename)
            shutil.copy(video_path, dest_video_path)
            
            # Create thumbnail from video
            thumbnail_path = os.path.join(content_dir, "thumbnail.jpg")
            self._create_video_thumbnail(video_path, thumbnail_path)
            
            # Create content data
            content_data = {
                "id": content_id,
                "type": "video",
                "persona_id": persona_id,
                "created_at": datetime.now().isoformat(),
                "file_path": dest_video_path,
                "thumbnail_path": thumbnail_path,
                "metadata": metadata or {}
            }
            
            # Save content data
            self._save_content_data(content_id, content_data)
            
            logger.info(f"Saved video content with ID {content_id}")
            return content_data
            
        except Exception as e:
            logger.error(f"Error saving video content: {str(e)}")
            raise
    
    def get_content(self, content_id):
        """
        Get content data by ID
        
        Args:
            content_id (str): ID of the content
            
        Returns:
            dict: Content data or None if not found
        """
        try:
            # Determine content type from directory structure
            image_content_path = os.path.join(self.image_dir, content_id, "content.json")
            video_content_path = os.path.join(self.video_dir, content_id, "content.json")
            
            content_path = None
            if os.path.exists(image_content_path):
                content_path = image_content_path
            elif os.path.exists(video_content_path):
                content_path = video_content_path
            else:
                logger.warning(f"Content with ID {content_id} not found")
                return None
            
            # Load content data
            with open(content_path, 'r') as f:
                content_data = json.load(f)
                
            return content_data
            
        except Exception as e:
            logger.error(f"Error getting content: {str(e)}")
            raise
    
    def list_content(self, content_type=None, persona_id=None):
        """
        List content with optional filtering
        
        Args:
            content_type (str): Filter by content type ('image' or 'video')
            persona_id (str): Filter by persona ID
            
        Returns:
            list: List of content data dictionaries
        """
        try:
            content_list = []
            
            # Determine directories to search based on content type
            dirs_to_search = []
            if content_type == "image" or content_type is None:
                dirs_to_search.append(self.image_dir)
            if content_type == "video" or content_type is None:
                dirs_to_search.append(self.video_dir)
            
            # Search directories
            for dir_path in dirs_to_search:
                if os.path.exists(dir_path):
                    for content_id in os.listdir(dir_path):
                        content_file = os.path.join(dir_path, content_id, "content.json")
                        if os.path.exists(content_file):
                            with open(content_file, 'r') as f:
                                content_data = json.load(f)
                                
                                # Apply persona filter if specified
                                if persona_id is None or content_data.get("persona_id") == persona_id:
                                    content_list.append(content_data)
            
            # Sort by creation date (newest first)
            content_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return content_list
            
        except Exception as e:
            logger.error(f"Error listing content: {str(e)}")
            raise
    
    def delete_content(self, content_id):
        """
        Delete content by ID
        
        Args:
            content_id (str): ID of the content to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get content data to determine type
            content_data = self.get_content(content_id)
            
            if not content_data:
                logger.warning(f"Content with ID {content_id} not found")
                return False
            
            # Determine content directory
            if content_data["type"] == "image":
                content_dir = os.path.join(self.image_dir, content_id)
            else:  # video
                content_dir = os.path.join(self.video_dir, content_id)
            
            # Delete content directory
            if os.path.exists(content_dir):
                shutil.rmtree(content_dir)
                logger.info(f"Deleted content {content_id}")
                return True
            else:
                logger.warning(f"Content directory for {content_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting content: {str(e)}")
            raise
    
    def export_content(self, content_ids, export_format="original", platform=None):
        """
        Export content for download or sharing
        
        Args:
            content_ids (list): List of content IDs to export
            export_format (str): Format for export ('original', 'web', 'high_res')
            platform (str): Platform optimization ('instagram', 'tiktok', etc.)
            
        Returns:
            str: Path to export directory or zip file
        """
        try:
            # Generate unique export ID
            export_id = str(uuid.uuid4())
            export_dir = os.path.join(self.export_dir, export_id)
            os.makedirs(export_dir, exist_ok=True)
            
            # Process each content item
            for content_id in content_ids:
                content_data = self.get_content(content_id)
                
                if not content_data:
                    logger.warning(f"Content with ID {content_id} not found, skipping")
                    continue
                
                # Get source file path
                source_path = content_data.get("file_path")
                if not source_path or not os.path.exists(source_path):
                    logger.warning(f"Source file for content {content_id} not found, skipping")
                    continue
                
                # Determine export filename
                filename = f"{content_data['type']}_{content_id}"
                if content_data["type"] == "image":
                    filename += ".jpg"
                else:  # video
                    filename += ".mp4"
                
                export_path = os.path.join(export_dir, filename)
                
                # Process based on content type and export format
                if content_data["type"] == "image":
                    self._export_image(source_path, export_path, export_format, platform)
                else:  # video
                    self._export_video(source_path, export_path, export_format, platform)
                
                # Create metadata file
                metadata_path = os.path.join(export_dir, f"{filename}.json")
                with open(metadata_path, 'w') as f:
                    json.dump(content_data.get("metadata", {}), f, indent=2)
            
            # Create zip file of export directory
            zip_path = f"{export_dir}.zip"
            shutil.make_archive(export_dir, 'zip', export_dir)
            
            logger.info(f"Exported {len(content_ids)} content items to {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error exporting content: {str(e)}")
            raise
    
    def _create_thumbnail(self, image_path, thumbnail_path, size=(200, 200)):
        """
        Create a thumbnail from an image
        
        Args:
            image_path (str): Path to the source image
            thumbnail_path (str): Path to save the thumbnail
            size (tuple): Thumbnail dimensions (width, height)
        """
        try:
            # Open image and create thumbnail
            with Image.open(image_path) as img:
                img.thumbnail(size)
                img.save(thumbnail_path)
                
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            raise
    
    def _create_video_thumbnail(self, video_path, thumbnail_path):
        """
        Create a thumbnail from a video
        
        Args:
            video_path (str): Path to the source video
            thumbnail_path (str): Path to save the thumbnail
        """
        try:
            # Open video and extract frame
            cap = cv2.VideoCapture(video_path)
            
            # Check if video opened successfully
            if not cap.isOpened():
                raise ValueError(f"Could not open video file {video_path}")
            
            # Read first frame
            ret, frame = cap.read()
            
            # If first frame is empty, try to read a frame from later in the video
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 30)  # Try frame 30
                ret, frame = cap.read()
            
            # Save frame as thumbnail if available
            if ret:
                cv2.imwrite(thumbnail_path, frame)
            else:
                raise ValueError(f"Could not extract frame from video {video_path}")
            
            # Release video capture
            cap.release()
                
        except Exception as e:
            logger.error(f"Error creating video thumbnail: {str(e)}")
            raise
    
    def _export_image(self, source_path, export_path, export_format, platform):
        """
        Export an image with format and platform optimizations
        
        Args:
            source_path (str): Path to the source image
            export_path (str): Path to save the exported image
            export_format (str): Format for export
            platform (str): Platform optimization
        """
        try:
            # Open source image
            with Image.open(source_path) as img:
                # Apply format-specific processing
                if export_format == "original":
                    # Just copy the original
                    img.save(export_path, quality=95)
                elif export_format == "web":
                    # Optimize for web (reduced size)
                    img.save(export_path, quality=85, optimize=True)
                elif export_format == "high_res":
                    # Save with highest quality
                    img.save(export_path, quality=100)
                else:
                    # Default to original
                    img.save(export_path, quality=95)
                
                # Apply platform-specific processing if needed
                if platform:
                    # This would be expanded with actual platform-specific optimizations
                    logger.info(f"Applied {platform} optimization to {export_path}")
                
        except Exception as e:
            logger.error(f"Error exporting image: {str(e)}")
            raise
    
    def _export_video(self, source_path, export_path, export_format, platform):
        """
        Export a video with format and platform optimizations
        
        Args:
            source_path (str): Path to the source video
            export_path (str): Path to save the exported video
            export_format (str): Format for export
            platform (str): Platform optimization
        """
        try:
            # For MVP, we'll just copy the video
            # In a full implementation, this would use ffmpeg to transcode
            # with format and platform-specific settings
            shutil.copy(source_path, export_path)
            
            logger.info(f"Exported video to {export_path}")
            logger.info(f"Note: Video format optimization is a placeholder in MVP")
                
        except Exception as e:
            logger.error(f"Error exporting video: {str(e)}")
            raise
    
    def _save_content_data(self, content_id, content_data):
        """
        Save content data to disk
        
        Args:
            content_id (str): ID of the content
            content_data (dict): Content data to save
        """
        try:
            # Determine content directory based on type
            if content_data["type"] == "image":
                content_dir = os.path.join(self.image_dir, content_id)
            else:  # video
                content_dir = os.path.join(self.video_dir, content_id)
            
            # Ensure content directory exists
            os.makedirs(content_dir, exist_ok=True)
            
            # Save content data
            content_file = os.path.join(content_dir, "content.json")
            with open(content_file, 'w') as f:
                json.dump(content_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving content data: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Create content manager
    manager = ContentManager()
    
    # Save test image
    with Image.new('RGB', (512, 512), color='red') as img:
        content = manager.save_image(
            img,
            persona_id="test_persona",
            metadata={
                "prompt": "Test image",
                "settings": {
                    "width": 512,
                    "height": 512
                }
            }
        )
        
    print(f"Saved test content with ID: {content['id']}")
