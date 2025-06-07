"""
Persona Management Module for AI Influencer Content Generator
Handles creation and storage of AI personas with consistent identity
"""

import os
import torch
import numpy as np
from PIL import Image
import logging
import json
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PersonaManager:
    """
    Manages AI personas for consistent identity across generations
    """
    
    def __init__(self, storage_dir="personas"):
        """
        Initialize the persona manager
        
        Args:
            storage_dir (str): Directory to store persona data
        """
        self.storage_dir = storage_dir
        
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        
        logger.info(f"Initialized PersonaManager with storage at {storage_dir}")
        
    def create_persona(self, name, reference_image=None, description=None, attributes=None):
        """
        Create a new persona from reference image or description
        
        Args:
            name (str): Name of the persona
            reference_image (PIL.Image or str): Reference image or path to image
            description (str): Text description of the persona
            attributes (dict): Additional attributes for the persona
            
        Returns:
            dict: Persona data including ID and paths
        """
        try:
            # Generate unique ID for persona
            persona_id = str(uuid.uuid4())
            
            # Create persona directory
            persona_dir = os.path.join(self.storage_dir, persona_id)
            os.makedirs(persona_dir, exist_ok=True)
            
            # Process reference image if provided
            reference_path = None
            if reference_image is not None:
                if isinstance(reference_image, str) and os.path.exists(reference_image):
                    # Copy reference image to persona directory
                    reference_path = os.path.join(persona_dir, "reference.jpg")
                    Image.open(reference_image).save(reference_path)
                elif isinstance(reference_image, Image.Image):
                    # Save PIL image to persona directory
                    reference_path = os.path.join(persona_dir, "reference.jpg")
                    reference_image.save(reference_path)
                else:
                    raise ValueError("Reference image must be a PIL Image or valid file path")
            
            # Create persona data
            persona_data = {
                "id": persona_id,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "reference_image": reference_path,
                "description": description,
                "attributes": attributes or {},
                "embedding_path": None  # Will be set when embedding is generated
            }
            
            # Save persona data
            self._save_persona_data(persona_id, persona_data)
            
            logger.info(f"Created persona {name} with ID {persona_id}")
            return persona_data
            
        except Exception as e:
            logger.error(f"Error creating persona: {str(e)}")
            raise
    
    def extract_identity_features(self, persona_id):
        """
        Extract identity features from reference image using InstantID
        
        Args:
            persona_id (str): ID of the persona
            
        Returns:
            dict: Updated persona data with embedding path
        """
        try:
            # Load persona data
            persona_data = self.get_persona(persona_id)
            
            if not persona_data:
                raise ValueError(f"Persona with ID {persona_id} not found")
                
            if not persona_data.get("reference_image"):
                raise ValueError(f"Persona {persona_id} has no reference image")
                
            # TODO: Implement actual InstantID integration
            # For MVP, we'll create a placeholder embedding
            logger.info(f"Extracting identity features for persona {persona_id}")
            
            # Create placeholder embedding
            embedding = np.random.randn(768).astype(np.float32)  # Typical embedding size
            
            # Save embedding
            embedding_path = os.path.join(self.storage_dir, persona_id, "embedding.npy")
            np.save(embedding_path, embedding)
            
            # Update persona data
            persona_data["embedding_path"] = embedding_path
            self._save_persona_data(persona_id, persona_data)
            
            logger.info(f"Identity features extracted for persona {persona_id}")
            return persona_data
            
        except Exception as e:
            logger.error(f"Error extracting identity features: {str(e)}")
            raise
    
    def get_persona(self, persona_id):
        """
        Get persona data by ID
        
        Args:
            persona_id (str): ID of the persona
            
        Returns:
            dict: Persona data or None if not found
        """
        try:
            # Check if persona exists
            persona_file = os.path.join(self.storage_dir, persona_id, "persona.json")
            if not os.path.exists(persona_file):
                logger.warning(f"Persona with ID {persona_id} not found")
                return None
                
            # Load persona data
            with open(persona_file, 'r') as f:
                persona_data = json.load(f)
                
            return persona_data
            
        except Exception as e:
            logger.error(f"Error getting persona: {str(e)}")
            raise
    
    def list_personas(self):
        """
        List all personas
        
        Returns:
            list: List of persona data dictionaries
        """
        try:
            personas = []
            
            # Iterate through persona directories
            for persona_id in os.listdir(self.storage_dir):
                persona_file = os.path.join(self.storage_dir, persona_id, "persona.json")
                if os.path.exists(persona_file):
                    with open(persona_file, 'r') as f:
                        persona_data = json.load(f)
                        personas.append(persona_data)
            
            return personas
            
        except Exception as e:
            logger.error(f"Error listing personas: {str(e)}")
            raise
    
    def update_persona(self, persona_id, updates):
        """
        Update persona attributes
        
        Args:
            persona_id (str): ID of the persona
            updates (dict): Dictionary of attributes to update
            
        Returns:
            dict: Updated persona data
        """
        try:
            # Get current persona data
            persona_data = self.get_persona(persona_id)
            
            if not persona_data:
                raise ValueError(f"Persona with ID {persona_id} not found")
                
            # Update attributes
            for key, value in updates.items():
                if key != "id":  # Don't allow changing ID
                    persona_data[key] = value
            
            # Save updated data
            self._save_persona_data(persona_id, persona_data)
            
            logger.info(f"Updated persona {persona_id}")
            return persona_data
            
        except Exception as e:
            logger.error(f"Error updating persona: {str(e)}")
            raise
    
    def delete_persona(self, persona_id):
        """
        Delete a persona
        
        Args:
            persona_id (str): ID of the persona to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if persona exists
            persona_dir = os.path.join(self.storage_dir, persona_id)
            if not os.path.exists(persona_dir):
                logger.warning(f"Persona with ID {persona_id} not found")
                return False
                
            # Delete persona directory
            import shutil
            shutil.rmtree(persona_dir)
            
            logger.info(f"Deleted persona {persona_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting persona: {str(e)}")
            raise
    
    def _save_persona_data(self, persona_id, persona_data):
        """
        Save persona data to disk
        
        Args:
            persona_id (str): ID of the persona
            persona_data (dict): Persona data to save
        """
        try:
            # Ensure persona directory exists
            persona_dir = os.path.join(self.storage_dir, persona_id)
            os.makedirs(persona_dir, exist_ok=True)
            
            # Save persona data
            persona_file = os.path.join(persona_dir, "persona.json")
            with open(persona_file, 'w') as f:
                json.dump(persona_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving persona data: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Create persona manager
    manager = PersonaManager()
    
    # Create persona
    persona = manager.create_persona(
        name="Test Persona",
        description="A test persona for development",
        attributes={
            "age_range": "25-35",
            "style": "Professional",
            "personality_traits": ["Confident", "Creative"]
        }
    )
    
    # Extract identity features
    manager.extract_identity_features(persona["id"])
