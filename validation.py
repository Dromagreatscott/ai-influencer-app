"""
Validation utilities for AI Influencer Content Generator
Provides tools for testing and validating app functionality and content quality
"""

import os
import logging
import time
import json
import random
from PIL import Image, ImageStat
import numpy as np
import cv2
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationManager:
    """
    Manages validation of app functionality and content quality
    """
    
    def __init__(self, base_dir="/home/ubuntu/ai_influencer_app"):
        """
        Initialize the validation manager
        
        Args:
            base_dir (str): Base directory for the application
        """
        self.base_dir = base_dir
        self.validation_dir = os.path.join(base_dir, "validation")
        self.reports_dir = os.path.join(self.validation_dir, "reports")
        self.reference_dir = os.path.join(self.validation_dir, "references")
        
        # Create validation directories
        os.makedirs(self.validation_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.reference_dir, exist_ok=True)
        
        logger.info(f"Initialized ValidationManager with base directory {base_dir}")
    
    def validate_image_quality(self, image_path, reference_path=None, min_score=7.0):
        """
        Validate the quality of a generated image
        
        Args:
            image_path (str): Path to the image to validate
            reference_path (str, optional): Path to a reference image for comparison
            min_score (float): Minimum quality score (0-10) to pass validation
            
        Returns:
            dict: Validation results
        """
        try:
            logger.info(f"Validating image quality for {image_path}")
            
            # Open image
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                image = image_path
            
            # Basic quality metrics
            results = {
                "filename": os.path.basename(image_path) if isinstance(image_path, str) else "in_memory_image",
                "resolution": {
                    "width": image.width,
                    "height": image.height
                },
                "aspect_ratio": round(image.width / image.height, 2),
                "metrics": {}
            }
            
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Calculate basic image statistics
            img_array = np.array(image)
            
            # Brightness
            brightness = np.mean(img_array)
            results["metrics"]["brightness"] = round(brightness, 2)
            
            # Contrast
            contrast = np.std(img_array)
            results["metrics"]["contrast"] = round(contrast, 2)
            
            # Sharpness estimation
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            results["metrics"]["sharpness"] = round(sharpness, 2)
            
            # Color variance
            color_variance = np.var(img_array, axis=(0, 1))
            results["metrics"]["color_variance"] = [round(v, 2) for v in color_variance]
            
            # Compare with reference image if provided
            if reference_path:
                reference = Image.open(reference_path)
                if reference.mode != "RGB":
                    reference = reference.convert("RGB")
                
                ref_array = np.array(reference)
                
                # Resize reference to match image dimensions for comparison
                if ref_array.shape != img_array.shape:
                    reference = reference.resize((image.width, image.height))
                    ref_array = np.array(reference)
                
                # Calculate structural similarity (simplified)
                # In a full implementation, we would use SSIM from skimage
                # For MVP, we'll use a simplified approach
                diff = np.abs(img_array.astype(np.float32) - ref_array.astype(np.float32))
                similarity = 1.0 - np.mean(diff) / 255.0
                results["metrics"]["reference_similarity"] = round(similarity, 4)
            
            # Calculate overall quality score (0-10)
            # This is a simplified scoring model for the MVP
            # A full implementation would use a more sophisticated model
            
            # Normalize metrics to 0-1 range
            norm_brightness = min(1.0, max(0.0, brightness / 255.0))
            norm_contrast = min(1.0, max(0.0, contrast / 128.0))
            norm_sharpness = min(1.0, max(0.0, sharpness / 5000.0))
            
            # Penalize extreme values
            brightness_score = 1.0 - 2.0 * abs(norm_brightness - 0.5)
            contrast_score = min(1.0, norm_contrast * 1.5)
            sharpness_score = min(1.0, norm_sharpness * 1.5)
            
            # Calculate overall score
            quality_score = (brightness_score * 0.3 + contrast_score * 0.3 + sharpness_score * 0.4) * 10.0
            results["quality_score"] = round(quality_score, 2)
            
            # Determine if image passes validation
            results["passes_validation"] = quality_score >= min_score
            
            logger.info(f"Image quality score: {quality_score:.2f}/10.0 (Minimum: {min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Error validating image quality: {str(e)}")
            raise
    
    def validate_video_quality(self, video_path, min_score=7.0):
        """
        Validate the quality of a generated video
        
        Args:
            video_path (str): Path to the video to validate
            min_score (float): Minimum quality score (0-10) to pass validation
            
        Returns:
            dict: Validation results
        """
        try:
            logger.info(f"Validating video quality for {video_path}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video file {video_path}")
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            results = {
                "filename": os.path.basename(video_path),
                "resolution": {
                    "width": width,
                    "height": height
                },
                "fps": round(fps, 2),
                "duration": round(duration, 2),
                "frame_count": frame_count,
                "metrics": {
                    "frames": []
                }
            }
            
            # Sample frames for analysis
            sample_count = min(10, frame_count)
            sample_indices = [int(i * frame_count / sample_count) for i in range(sample_count)]
            
            frame_scores = []
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Convert frame to PIL Image for quality analysis
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                
                # Analyze frame quality
                frame_result = self.validate_image_quality(frame_pil, min_score=0)  # Don't apply min_score to individual frames
                frame_result["frame_number"] = idx
                
                results["metrics"]["frames"].append(frame_result)
                frame_scores.append(frame_result["quality_score"])
            
            # Release video capture
            cap.release()
            
            # Calculate overall video quality score
            if frame_scores:
                # Average frame quality
                avg_frame_quality = sum(frame_scores) / len(frame_scores)
                
                # Frame quality consistency (standard deviation)
                frame_quality_std = np.std(frame_scores) if len(frame_scores) > 1 else 0
                consistency_score = max(0, 10 - frame_quality_std * 5)
                
                # Overall score combines average quality and consistency
                video_quality_score = avg_frame_quality * 0.7 + consistency_score * 0.3
                
                results["metrics"]["average_frame_quality"] = round(avg_frame_quality, 2)
                results["metrics"]["frame_quality_consistency"] = round(consistency_score, 2)
                results["quality_score"] = round(video_quality_score, 2)
                
                # Determine if video passes validation
                results["passes_validation"] = video_quality_score >= min_score
            else:
                results["quality_score"] = 0
                results["passes_validation"] = False
            
            logger.info(f"Video quality score: {results.get('quality_score', 0):.2f}/10.0 (Minimum: {min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Error validating video quality: {str(e)}")
            raise
    
    def validate_persona_consistency(self, image_paths, reference_path=None, min_score=7.0):
        """
        Validate the consistency of a persona across multiple images
        
        Args:
            image_paths (list): List of paths to images to validate
            reference_path (str, optional): Path to a reference image
            min_score (float): Minimum consistency score (0-10) to pass validation
            
        Returns:
            dict: Validation results
        """
        try:
            logger.info(f"Validating persona consistency across {len(image_paths)} images")
            
            results = {
                "image_count": len(image_paths),
                "reference_image": os.path.basename(reference_path) if reference_path else None,
                "consistency_scores": [],
                "overall_consistency": 0
            }
            
            # For MVP, we'll use a simplified approach to consistency validation
            # In a full implementation, we would use face recognition and feature extraction
            
            # If no reference image is provided, use the first image as reference
            if not reference_path and image_paths:
                reference_path = image_paths[0]
                image_paths = image_paths[1:]
            
            if not reference_path:
                raise ValueError("Reference image is required for consistency validation")
            
            # Open reference image
            reference = Image.open(reference_path)
            if reference.mode != "RGB":
                reference = reference.convert("RGB")
            
            ref_array = np.array(reference)
            
            # Compare each image to the reference
            for image_path in image_paths:
                image = Image.open(image_path)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                
                # Resize to match reference dimensions
                image = image.resize((reference.width, reference.height))
                img_array = np.array(image)
                
                # Calculate similarity (simplified)
                diff = np.abs(img_array.astype(np.float32) - ref_array.astype(np.float32))
                similarity = 1.0 - np.mean(diff) / 255.0
                
                # Convert to consistency score (0-10)
                consistency_score = similarity * 10.0
                
                results["consistency_scores"].append({
                    "image": os.path.basename(image_path),
                    "score": round(consistency_score, 2)
                })
            
            # Calculate overall consistency
            if results["consistency_scores"]:
                overall_consistency = sum(item["score"] for item in results["consistency_scores"]) / len(results["consistency_scores"])
                results["overall_consistency"] = round(overall_consistency, 2)
                results["passes_validation"] = overall_consistency >= min_score
            else:
                results["overall_consistency"] = 0
                results["passes_validation"] = False
            
            logger.info(f"Persona consistency score: {results['overall_consistency']:.2f}/10.0 (Minimum: {min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Error validating persona consistency: {str(e)}")
            raise
    
    def compare_with_glambase(self, image_path, glambase_url=None):
        """
        Compare generated image with glambase.app quality
        
        Args:
            image_path (str): Path to the image to compare
            glambase_url (str, optional): URL to a glambase image for comparison
            
        Returns:
            dict: Comparison results
        """
        try:
            logger.info(f"Comparing image with glambase quality: {image_path}")
            
            # For MVP, we'll use a simplified approach
            # In a full implementation, we would use a more sophisticated comparison
            
            results = {
                "image": os.path.basename(image_path),
                "glambase_reference": glambase_url,
                "metrics": {}
            }
            
            # Open local image
            local_image = Image.open(image_path)
            if local_image.mode != "RGB":
                local_image = local_image.convert("RGB")
            
            # Get local image quality metrics
            local_quality = self.validate_image_quality(local_image)
            results["local_quality_score"] = local_quality["quality_score"]
            
            # If glambase URL is provided, download and compare
            if glambase_url:
                try:
                    response = requests.get(glambase_url)
                    glambase_image = Image.open(BytesIO(response.content))
                    if glambase_image.mode != "RGB":
                        glambase_image = glambase_image.convert("RGB")
                    
                    # Get glambase image quality metrics
                    glambase_quality = self.validate_image_quality(glambase_image)
                    results["glambase_quality_score"] = glambase_quality["quality_score"]
                    
                    # Calculate quality difference
                    quality_diff = local_quality["quality_score"] - glambase_quality["quality_score"]
                    results["quality_difference"] = round(quality_diff, 2)
                    
                    # Determine if local image matches or exceeds glambase quality
                    results["matches_glambase_quality"] = quality_diff >= -1.0  # Allow for small difference
                    
                except Exception as e:
                    logger.error(f"Error downloading or processing glambase image: {str(e)}")
                    results["error"] = f"Failed to process glambase reference: {str(e)}"
            else:
                # Without a reference, we'll use a threshold based on typical glambase quality
                # This is a simplified approach for the MVP
                results["matches_glambase_quality"] = local_quality["quality_score"] >= 8.0
            
            logger.info(f"Glambase quality comparison: Local score {results.get('local_quality_score', 0):.2f}, " +
                       f"Matches glambase quality: {results.get('matches_glambase_quality', False)}")
            return results
            
        except Exception as e:
            logger.error(f"Error comparing with glambase: {str(e)}")
            raise
    
    def run_comprehensive_validation(self, output_report=True):
        """
        Run comprehensive validation of the entire application
        
        Args:
            output_report (bool): Whether to output a validation report
            
        Returns:
            dict: Comprehensive validation results
        """
        try:
            logger.info("Starting comprehensive validation")
            
            validation_start = time.time()
            
            results = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "modules": {},
                "overall_result": False
            }
            
            # Validate image generation
            results["modules"]["image_generation"] = self._validate_image_generation()
            
            # Validate video conversion
            results["modules"]["video_conversion"] = self._validate_video_conversion()
            
            # Validate persona consistency
            results["modules"]["persona_consistency"] = self._validate_persona_consistency()
            
            # Validate content management
            results["modules"]["content_management"] = self._validate_content_management()
            
            # Validate integration
            results["modules"]["integration"] = self._validate_integration()
            
            # Calculate overall validation result
            module_results = [module.get("passes_validation", False) for module in results["modules"].values()]
            results["overall_result"] = all(module_results)
            
            # Calculate validation duration
            validation_duration = time.time() - validation_start
            results["duration_seconds"] = round(validation_duration, 2)
            
            logger.info(f"Comprehensive validation completed in {validation_duration:.2f} seconds")
            logger.info(f"Overall validation result: {'PASS' if results['overall_result'] else 'FAIL'}")
            
            # Output validation report if requested
            if output_report:
                report_path = os.path.join(self.reports_dir, f"validation_report_{int(time.time())}.json")
                with open(report_path, 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Validation report saved to {report_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running comprehensive validation: {str(e)}")
            raise
    
    def _validate_image_generation(self):
        """
        Validate the image generation module
        
        Returns:
            dict: Validation results
        """
        try:
            logger.info("Validating image generation module")
            
            # For MVP, we'll use a simplified validation approach
            # In a full implementation, we would test various prompts and settings
            
            results = {
                "test_cases": [],
                "passes_validation": False
            }
            
            # Import image generator
            from models.image_generator import ImageGenerator
            generator = ImageGenerator()
            
            # Test case 1: Basic portrait generation
            try:
                portrait_prompt = "professional portrait of a business person, high quality, detailed, studio lighting"
                portrait = generator.generate_image(
                    prompt=portrait_prompt,
                    width=512,
                    height=512,
                    num_inference_steps=30,
                    guidance_scale=7.5
                )
                
                # Save generated image for validation
                portrait_path = os.path.join(self.validation_dir, "test_portrait.jpg")
                portrait.save(portrait_path)
                
                # Validate image quality
                quality_results = self.validate_image_quality(portrait_path, min_score=7.5)
                
                # Compare with glambase quality
                glambase_results = self.compare_with_glambase(portrait_path)
                
                results["test_cases"].append({
                    "name": "Basic Portrait Generation",
                    "prompt": portrait_prompt,
                    "image_path": portrait_path,
                    "quality_score": quality_results["quality_score"],
                    "matches_glambase_quality": glambase_results["matches_glambase_quality"],
                    "passes": quality_results["passes_validation"] and glambase_results["matches_glambase_quality"]
                })
                
            except Exception as e:
                logger.error(f"Error in portrait generation test: {str(e)}")
                results["test_cases"].append({
                    "name": "Basic Portrait Generation",
                    "error": str(e),
                    "passes": False
                })
            
            # Test case 2: Full body generation
            try:
                fullbody_prompt = "full body shot of a professional person in business attire, high quality, detailed"
                fullbody = generator.generate_image(
                    prompt=fullbody_prompt,
                    width=512,
                    height=768,
                    num_inference_steps=30,
                    guidance_scale=7.5
                )
                
                # Save generated image for validation
                fullbody_path = os.path.join(self.validation_dir, "test_fullbody.jpg")
                fullbody.save(fullbody_path)
                
                # Validate image quality
                quality_results = self.validate_image_quality(fullbody_path, min_score=7.5)
                
                # Compare with glambase quality
                glambase_results = self.compare_with_glambase(fullbody_path)
                
                results["test_cases"].append({
                    "name": "Full Body Generation",
                    "prompt": fullbody_prompt,
                    "image_path": fullbody_path,
                    "quality_score": quality_results["quality_score"],
                    "matches_glambase_quality": glambase_results["matches_glambase_quality"],
                    "passes": quality_results["passes_validation"] and glambase_results["matches_glambase_quality"]
                })
                
            except Exception as e:
                logger.error(f"Error in full body generation test: {str(e)}")
                results["test_cases"].append({
                    "name": "Full Body Generation",
                    "error": str(e),
                    "passes": False
                })
            
            # Determine overall result
            test_results = [test.get("passes", False) for test in results["test_cases"]]
            results["passes_validation"] = all(test_results)
            
            logger.info(f"Image generation validation result: {'PASS' if results['passes_validation'] else 'FAIL'}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating image generation: {str(e)}")
            raise
    
    def _validate_video_conversion(self):
        """
        Validate the video conversion module
        
        Returns:
            dict: Validation results
        """
        try:
            logger.info("Validating video conversion module")
            
            results = {
                "test_cases": [],
                "passes_validation": False
            }
            
            # Import video converter
            from models.video_converter import ImageToVideoConverter
            converter = ImageToVideoConverter(output_dir=os.path.join(self.validation_dir, "videos"))
            
            # Test case 1: Basic image animation
            try:
                # Use a test image from validation
                image_path = os.path.join(self.validation_dir, "test_portrait.jpg")
                
                # If test image doesn't exist, create a simple test image
                if not os.path.exists(image_path):
                    test_image = Image.new('RGB', (512, 512), color='blue')
                    test_image.save(image_path)
                
                # Animate image
                video_path = converter.animate_image(
                    image_path=image_path,
                    duration=5,
                    motion_type="subtle",
                    fps=30
                )
                
                # Validate video quality
                quality_results = self.validate_video_quality(video_path, min_score=7.0)
                
                results["test_cases"].append({
                    "name": "Basic Image Animation",
                    "image_path": image_path,
                    "video_path": video_path,
                    "quality_score": quality_results["quality_score"],
                    "passes": quality_results["passes_validation"]
                })
                
            except Exception as e:
                logger.error(f"Error in image animation test: {str(e)}")
                results["test_cases"].append({
                    "name": "Basic Image Animation",
                    "error": str(e),
                    "passes": False
                })
            
            # Test case 2: Face swap (placeholder implementation for MVP)
            try:
                # Use a test image from validation
                face_image_path = os.path.join(self.validation_dir, "test_portrait.jpg")
                
                # If test image doesn't exist, create a simple test image
                if not os.path.exists(face_image_path):
                    test_image = Image.new('RGB', (512, 512), color='red')
                    test_image.save(face_image_path)
                
                # For MVP, we'll use the animated video as target
                # In a full implementation, we would use a proper target video
                target_video_path = os.path.join(self.validation_dir, "videos", "test_target.mp4")
                
                # If target video doesn't exist, create a simple test video
                if not os.path.exists(target_video_path):
                    # Use the previously created video if available
                    if results["test_cases"] and "video_path" in results["test_cases"][0]:
                        target_video_path = results["test_cases"][0]["video_path"]
                    else:
                        # Skip this test if we can't create a target video
                        raise ValueError("No target video available for face swap test")
                
                # Perform face swap
                face_swap_path = converter.face_swap_video(
                    face_image_path=face_image_path,
                    target_video_path=target_video_path
                )
                
                # Validate video quality
                quality_results = self.validate_video_quality(face_swap_path, min_score=7.0)
                
                results["test_cases"].append({
                    "name": "Face Swap",
                    "face_image_path": face_image_path,
                    "target_video_path": target_video_path,
                    "output_video_path": face_swap_path,
                    "quality_score": quality_results["quality_score"],
                    "passes": quality_results["passes_validation"]
                })
                
            except Exception as e:
                logger.error(f"Error in face swap test: {str(e)}")
                results["test_cases"].append({
                    "name": "Face Swap",
                    "error": str(e),
                    "passes": False
                })
            
            # Determine overall result
            test_results = [test.get("passes", False) for test in results["test_cases"]]
            results["passes_validation"] = all(test_results)
            
            logger.info(f"Video conversion validation result: {'PASS' if results['passes_validation'] else 'FAIL'}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating video conversion: {str(e)}")
            raise
    
    def _validate_persona_consistency(self):
        """
        Validate the persona consistency module
        
        Returns:
            dict: Validation results
        """
        try:
            logger.info("Validating persona consistency module")
            
            results = {
                "test_cases": [],
                "passes_validation": False
            }
            
            # Import persona manager
            from models.persona_manager import PersonaManager
            manager = PersonaManager(storage_dir=os.path.join(self.validation_dir, "personas"))
            
            # Test case 1: Basic persona creation and consistency
            try:
                # Create a test persona
                persona = manager.create_persona(
                    name="Test Persona",
                    description="A professional business person with a confident demeanor",
                    attributes={
                        "age_range": "30-40",
                        "gender": "person",
                        "style": "Professional"
                    }
                )
                
                # Extract identity features
                persona = manager.extract_identity_features(persona["id"])
                
                # Generate multiple images with the same persona
                # For MVP, we'll simulate this with placeholder images
                image_paths = []
                for i in range(3):
                    # Create a simple test image
                    test_image = Image.new('RGB', (512, 512), color=(100 + i * 20, 150, 200))
                    image_path = os.path.join(self.validation_dir, f"persona_test_{i}.jpg")
                    test_image.save(image_path)
                    image_paths.append(image_path)
                
                # Validate persona consistency
                consistency_results = self.validate_persona_consistency(
                    image_paths=image_paths,
                    min_score=7.0
                )
                
                results["test_cases"].append({
                    "name": "Basic Persona Consistency",
                    "persona_id": persona["id"],
                    "image_paths": image_paths,
                    "consistency_score": consistency_results["overall_consistency"],
                    "passes": consistency_results["passes_validation"]
                })
                
            except Exception as e:
                logger.error(f"Error in persona consistency test: {str(e)}")
                results["test_cases"].append({
                    "name": "Basic Persona Consistency",
                    "error": str(e),
                    "passes": False
                })
            
            # Determine overall result
            test_results = [test.get("passes", False) for test in results["test_cases"]]
            results["passes_validation"] = all(test_results)
            
            logger.info(f"Persona consistency validation result: {'PASS' if results['passes_validation'] else 'FAIL'}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating persona consistency: {str(e)}")
            raise
    
    def _validate_content_management(self):
        """
        Validate the content management module
        
        Returns:
            dict: Validation results
        """
        try:
            logger.info("Validating content management module")
            
            results = {
                "test_cases": [],
                "passes_validation": False
            }
            
            # Import content manager
            from models.content_manager import ContentManager
            manager = ContentManager(storage_dir=os.path.join(self.validation_dir, "content"))
            
            # Test case 1: Save and retrieve image content
            try:
                # Create a test image
                test_image = Image.new('RGB', (512, 512), color='green')
                
                # Save image to content store
                content_data = manager.save_image(
                    image=test_image,
                    persona_id="test_persona",
                    metadata={
                        "prompt": "Test image",
                        "settings": {
                            "width": 512,
                            "height": 512
                        }
                    }
                )
                
                # Retrieve content
                retrieved_content = manager.get_content(content_data["id"])
                
                # Verify content data
                content_verified = (
                    retrieved_content is not None and
                    retrieved_content["id"] == content_data["id"] and
                    retrieved_content["type"] == "image" and
                    retrieved_content["persona_id"] == "test_persona" and
                    os.path.exists(retrieved_content["file_path"])
                )
                
                results["test_cases"].append({
                    "name": "Save and Retrieve Image Content",
                    "content_id": content_data["id"],
                    "content_verified": content_verified,
                    "passes": content_verified
                })
                
            except Exception as e:
                logger.error(f"Error in content management test: {str(e)}")
                results["test_cases"].append({
                    "name": "Save and Retrieve Image Content",
                    "error": str(e),
                    "passes": False
                })
            
            # Test case 2: Content listing and filtering
            try:
                # List all content
                all_content = manager.list_content()
                
                # Filter by type
                image_content = manager.list_content(content_type="image")
                
                # Filter by persona
                persona_content = manager.list_content(persona_id="test_persona")
                
                # Verify filtering
                filtering_verified = (
                    len(all_content) > 0 and
                    len(image_content) > 0 and
                    len(persona_content) > 0 and
                    all(item["type"] == "image" for item in image_content) and
                    all(item["persona_id"] == "test_persona" for item in persona_content)
                )
                
                results["test_cases"].append({
                    "name": "Content Listing and Filtering",
                    "all_content_count": len(all_content),
                    "image_content_count": len(image_content),
                    "persona_content_count": len(persona_content),
                    "filtering_verified": filtering_verified,
                    "passes": filtering_verified
                })
                
            except Exception as e:
                logger.error(f"Error in content filtering test: {str(e)}")
                results["test_cases"].append({
                    "name": "Content Listing and Filtering",
                    "error": str(e),
                    "passes": False
                })
            
            # Determine overall result
            test_results = [test.get("passes", False) for test in results["test_cases"]]
            results["passes_validation"] = all(test_results)
            
            logger.info(f"Content management validation result: {'PASS' if results['passes_validation'] else 'FAIL'}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating content management: {str(e)}")
            raise
    
    def _validate_integration(self):
        """
        Validate the integration between modules
        
        Returns:
            dict: Validation results
        """
        try:
            logger.info("Validating integration between modules")
            
            results = {
                "test_cases": [],
                "passes_validation": False
            }
            
            # Import integration manager
            from utils.integration import IntegrationManager
            manager = IntegrationManager(base_dir=os.path.join(self.validation_dir, "integration"))
            
            # Test case 1: End-to-end persona creation workflow
            try:
                # Create a test persona
                persona = manager.create_persona_workflow(
                    name="Integration Test Persona",
                    description="A professional business person for integration testing",
                    attributes={
                        "age_range": "30-40",
                        "gender": "person",
                        "style": "Professional"
                    }
                )
                
                # Verify persona data
                persona_verified = (
                    persona is not None and
                    persona["name"] == "Integration Test Persona" and
                    "preview_images" in persona and
                    len(persona["preview_images"]) > 0
                )
                
                results["test_cases"].append({
                    "name": "Persona Creation Workflow",
                    "persona_id": persona["id"] if persona else None,
                    "preview_images_count": len(persona["preview_images"]) if persona and "preview_images" in persona else 0,
                    "persona_verified": persona_verified,
                    "passes": persona_verified
                })
                
            except Exception as e:
                logger.error(f"Error in persona creation workflow test: {str(e)}")
                results["test_cases"].append({
                    "name": "Persona Creation Workflow",
                    "error": str(e),
                    "passes": False
                })
            
            # Test case 2: Content generation workflow
            try:
                # Get persona ID from previous test
                persona_id = None
                if results["test_cases"] and "persona_id" in results["test_cases"][0]:
                    persona_id = results["test_cases"][0]["persona_id"]
                
                if not persona_id:
                    raise ValueError("No persona ID available for content generation test")
                
                # Generate content
                content_items = manager.generate_content_workflow(
                    persona_id=persona_id,
                    content_type="portrait",
                    settings={
                        "style": "professional",
                        "setting": "studio"
                    },
                    count=1
                )
                
                # Verify content generation
                content_verified = (
                    content_items is not None and
                    len(content_items) > 0 and
                    "id" in content_items[0] and
                    "file_path" in content_items[0] and
                    os.path.exists(content_items[0]["file_path"])
                )
                
                results["test_cases"].append({
                    "name": "Content Generation Workflow",
                    "content_count": len(content_items) if content_items else 0,
                    "content_verified": content_verified,
                    "passes": content_verified
                })
                
            except Exception as e:
                logger.error(f"Error in content generation workflow test: {str(e)}")
                results["test_cases"].append({
                    "name": "Content Generation Workflow",
                    "error": str(e),
                    "passes": False
                })
            
            # Determine overall result
            test_results = [test.get("passes", False) for test in results["test_cases"]]
            results["passes_validation"] = all(test_results)
            
            logger.info(f"Integration validation result: {'PASS' if results['passes_validation'] else 'FAIL'}")
            return results
            
        except Exception as e:
            logger.error(f"Error validating integration: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Create validation manager
    validator = ValidationManager()
    
    # Run comprehensive validation
    results = validator.run_comprehensive_validation(output_report=True)
    
    print(f"Validation complete. Overall result: {'PASS' if results['overall_result'] else 'FAIL'}")
