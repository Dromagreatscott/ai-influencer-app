"""
Main application file for AI Influencer Content Generator
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import json
import time
from PIL import Image

# Import core modules
from models.image_generator import ImageGenerator
from models.persona_manager import PersonaManager
from models.video_converter import ImageToVideoConverter
from models.content_manager import ContentManager
from utils.integration import IntegrationManager
from utils.validation import ValidationManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize core modules
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

integration_manager = IntegrationManager(base_dir=base_dir)
validation_manager = ValidationManager(base_dir=base_dir)

# Create placeholder images for development
def create_placeholder_images():
    static_img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')
    os.makedirs(static_img_dir, exist_ok=True)
    
    # Create placeholder image if it doesn't exist
    placeholder_path = os.path.join(static_img_dir, 'placeholder.jpg')
    if not os.path.exists(placeholder_path):
        placeholder = Image.new('RGB', (512, 512), color=(100, 149, 237))
        placeholder.save(placeholder_path)
    
    # Create example images
    for i in range(1, 4):
        example_path = os.path.join(static_img_dir, f'example-{i}.jpg')
        if not os.path.exists(example_path):
            color = (100 + i * 30, 149, 237 - i * 20)
            example = Image.new('RGB', (512, 512), color=color)
            example.save(example_path)
    
    # Create hero image
    hero_path = os.path.join(static_img_dir, 'hero-image.jpg')
    if not os.path.exists(hero_path):
        hero = Image.new('RGB', (800, 600), color=(70, 130, 180))
        hero.save(hero_path)
    
    # Create videos directory
    static_video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'videos')
    os.makedirs(static_video_dir, exist_ok=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Get personas and recent content
    # For MVP, we'll use placeholder data
    personas = [
        {"id": "1", "name": "Business Professional", "image": url_for('static', filename='img/placeholder.jpg')},
        {"id": "2", "name": "Creative Artist", "image": url_for('static', filename='img/placeholder.jpg')},
        {"id": "3", "name": "Fitness Instructor", "image": url_for('static', filename='img/placeholder.jpg')}
    ]
    
    recent_content = [
        {"id": "1", "type": "image", "path": url_for('static', filename='img/example-1.jpg')},
        {"id": "2", "type": "image", "path": url_for('static', filename='img/example-2.jpg')},
        {"id": "3", "type": "video", "path": url_for('static', filename='img/example-3.jpg')}
    ]
    
    return render_template('dashboard.html', personas=personas, recent_content=recent_content)

@app.route('/personas')
def personas():
    # Get all personas
    # For MVP, we'll use placeholder data
    personas = [
        {
            "id": "1", 
            "name": "Business Professional", 
            "image": url_for('static', filename='img/placeholder.jpg'),
            "description": "Professional business persona for corporate content",
            "attributes": {"age_range": "30-40", "style": "Professional"}
        },
        {
            "id": "2", 
            "name": "Creative Artist", 
            "image": url_for('static', filename='img/placeholder.jpg'),
            "description": "Creative and artistic persona for social media",
            "attributes": {"age_range": "25-35", "style": "Artistic"}
        },
        {
            "id": "3", 
            "name": "Fitness Instructor", 
            "image": url_for('static', filename='img/placeholder.jpg'),
            "description": "Fitness and wellness focused persona",
            "attributes": {"age_range": "25-35", "style": "Athletic"}
        }
    ]
    
    return render_template('personas.html', personas=personas)

@app.route('/create-persona', methods=['GET', 'POST'])
def create_persona():
    if request.method == 'POST':
        # Process form data
        name = request.form.get('name')
        description = request.form.get('description')
        age_range = request.form.get('age_range')
        style = request.form.get('style')
        
        # Process reference image if provided
        reference_image = None
        if 'reference_image' in request.files:
            file = request.files['reference_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                reference_image = filepath
        
        # Collect attributes
        attributes = {
            "age_range": age_range,
            "style": style
        }
        
        # Process personality traits
        if 'personality_traits' in request.form:
            attributes["personality_traits"] = request.form.getlist('personality_traits')
        
        # Add additional notes if provided
        if request.form.get('additional_notes'):
            attributes["additional_notes"] = request.form.get('additional_notes')
        
        try:
            # Create persona
            # For MVP, we'll simulate this without actually calling the integration manager
            # persona = integration_manager.create_persona_workflow(
            #     name=name,
            #     reference_image=reference_image,
            #     description=description,
            #     attributes=attributes
            # )
            
            # Simulate success
            flash('Persona created successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Error creating persona: {str(e)}")
            flash(f'Error creating persona: {str(e)}', 'error')
    
    return render_template('create_persona.html')

@app.route('/generate-content', methods=['GET', 'POST'])
def generate_content():
    # Get personas for selection
    # For MVP, we'll use placeholder data
    personas = [
        {"id": "1", "name": "Business Professional"},
        {"id": "2", "name": "Creative Artist"},
        {"id": "3", "name": "Fitness Instructor"}
    ]
    
    if request.method == 'POST':
        # Process form data
        persona_id = request.form.get('persona_id')
        content_type = request.form.get('content_type')
        setting = request.form.get('setting')
        additional_prompt = request.form.get('additional_prompt')
        quantity = int(request.form.get('quantity', 4))
        quality = request.form.get('quality')
        
        # Collect settings
        settings = {
            "setting": setting,
            "additional_prompt": additional_prompt,
            "quality": quality
        }
        
        try:
            # Generate content
            # For MVP, we'll simulate this without actually calling the integration manager
            # content_items = integration_manager.generate_content_workflow(
            #     persona_id=persona_id,
            #     content_type=content_type,
            #     settings=settings,
            #     count=quantity
            # )
            
            # Simulate success
            flash('Content generated successfully!', 'success')
            return redirect(url_for('gallery'))
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            flash(f'Error generating content: {str(e)}', 'error')
    
    return render_template('generate_content.html', personas=personas)

@app.route('/create-video', methods=['GET', 'POST'])
def create_video():
    if request.method == 'POST':
        # Process form data
        image_id = request.form.get('image_id')
        video_type = request.form.get('video_type')
        motion_type = request.form.get('motion_type')
        duration = int(request.form.get('duration', 5))
        quality = request.form.get('quality')
        
        # Additional settings for face swap
        target_video = None
        if video_type == 'face_swap':
            target_video = request.form.get('target_video')
        
        # Collect settings
        settings = {
            "motion_type": motion_type,
            "duration": duration,
            "quality": quality
        }
        
        if target_video:
            settings["target_video"] = target_video
        
        try:
            # Create video
            # For MVP, we'll simulate this without actually calling the integration manager
            # video_content = integration_manager.create_video_workflow(
            #     image_id=image_id,
            #     video_type=video_type,
            #     settings=settings
            # )
            
            # Simulate success
            flash('Video created successfully!', 'success')
            return redirect(url_for('gallery'))
            
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            flash(f'Error creating video: {str(e)}', 'error')
    
    return render_template('create_video.html')

@app.route('/gallery')
def gallery():
    # Get all content
    # For MVP, we'll use placeholder data
    content_items = [
        {"id": "1", "type": "image", "path": url_for('static', filename='img/example-1.jpg'), "created_at": "2025-06-01"},
        {"id": "2", "type": "image", "path": url_for('static', filename='img/example-2.jpg'), "created_at": "2025-06-01"},
        {"id": "3", "type": "video", "path": url_for('static', filename='img/example-3.jpg'), "created_at": "2025-06-01"},
        {"id": "4", "type": "image", "path": url_for('static', filename='img/placeholder.jpg'), "created_at": "2025-06-01"}
    ]
    
    return render_template('gallery.html', content_items=content_items)

@app.route('/export', methods=['GET', 'POST'])
def export():
    if request.method == 'POST':
        # Process form data
        content_ids = request.form.getlist('content_ids')
        export_format = request.form.get('export_format')
        platform = request.form.get('platform')
        
        try:
            # Export content
            # For MVP, we'll simulate this without actually calling the integration manager
            # export_path = integration_manager.export_workflow(
            #     content_ids=content_ids,
            #     export_format=export_format,
            #     platform=platform
            # )
            
            # Simulate success
            flash('Content exported successfully!', 'success')
            return redirect(url_for('gallery'))
            
        except Exception as e:
            logger.error(f"Error exporting content: {str(e)}")
            flash(f'Error exporting content: {str(e)}', 'error')
    
    # Get content for selection
    # For MVP, we'll use placeholder data
    content_items = [
        {"id": "1", "type": "image", "path": url_for('static', filename='img/example-1.jpg'), "created_at": "2025-06-01"},
        {"id": "2", "type": "image", "path": url_for('static', filename='img/example-2.jpg'), "created_at": "2025-06-01"},
        {"id": "3", "type": "video", "path": url_for('static', filename='img/example-3.jpg'), "created_at": "2025-06-01"}
    ]
    
    return render_template('export.html', content_items=content_items)

@app.route('/validate')
def validate():
    try:
        # Run validation
        results = validation_manager.run_comprehensive_validation(output_report=True)
        return render_template('validation.html', results=results)
        
    except Exception as e:
        logger.error(f"Error running validation: {str(e)}")
        flash(f'Error running validation: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/personas', methods=['GET'])
def api_personas():
    # Get all personas
    # For MVP, we'll use placeholder data
    personas = [
        {"id": "1", "name": "Business Professional"},
        {"id": "2", "name": "Creative Artist"},
        {"id": "3", "name": "Fitness Instructor"}
    ]
    
    return jsonify(personas)

@app.route('/api/content', methods=['GET'])
def api_content():
    # Get all content
    # For MVP, we'll use placeholder data
    content_items = [
        {"id": "1", "type": "image", "path": url_for('static', filename='img/example-1.jpg'), "created_at": "2025-06-01"},
        {"id": "2", "type": "image", "path": url_for('static', filename='img/example-2.jpg'), "created_at": "2025-06-01"},
        {"id": "3", "type": "video", "path": url_for('static', filename='img/example-3.jpg'), "created_at": "2025-06-01"}
    ]
    
    return jsonify(content_items)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create placeholder images for development
    create_placeholder_images()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
