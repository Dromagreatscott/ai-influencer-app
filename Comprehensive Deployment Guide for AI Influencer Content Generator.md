# Comprehensive Deployment Guide for AI Influencer Content Generator

This guide provides detailed instructions for deploying the AI Influencer Content Generator application in both local and cloud environments. Follow these steps to get your application up and running and make it accessible to users.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Cloud Deployment Options](#cloud-deployment-options)
   - [Heroku Deployment](#heroku-deployment)
   - [AWS Deployment](#aws-deployment)
   - [Google Cloud Platform Deployment](#google-cloud-platform-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Model Deployment](#model-deployment)
7. [Scaling Considerations](#scaling-considerations)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the application, ensure you have the following prerequisites installed:

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment tool (venv or conda)
- FFmpeg (for video processing)
- Node.js and npm (for frontend assets, if applicable)

For cloud deployments, you'll also need:
- Account with your chosen cloud provider (AWS, GCP, Heroku, etc.)
- Cloud provider CLI tools installed and configured
- Docker (for containerized deployments)

## Local Deployment

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ai-influencer-app.git
cd ai-influencer-app
```

If you don't have a Git repository, create a directory and copy all project files there:

```bash
mkdir ai-influencer-app
cp -r /path/to/project/* ai-influencer-app/
cd ai-influencer-app
```

### Step 2: Set Up Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n ai-influencer-env python=3.8
conda activate ai-influencer-env
```

### Step 3: Install Dependencies

```bash
pip install -r src/requirements.txt
```

### Step 4: Create Data Directories

```bash
mkdir -p data/personas data/content data/uploads data/exports
```

### Step 5: Download Model Weights

For the MVP, you'll need to download the necessary model weights for image generation and face processing:

```bash
# Create models directory
mkdir -p models

# Download model weights (example commands - adjust based on actual models used)
# For Stable Diffusion
python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', use_safetensors=True).save_pretrained('./models/sdxl')"

# For face detection/recognition
pip install gdown
gdown --id YOUR_GOOGLE_DRIVE_ID -O ./models/face_detection.pth
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following environment variables:

```
FLASK_APP=src/app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
MODEL_PATH=./models
DATA_PATH=./data
```

### Step 7: Run the Application

```bash
flask run --host=0.0.0.0 --port=5000
```

The application will be available at `http://localhost:5000`.

## Cloud Deployment Options

### Heroku Deployment

Heroku is one of the simplest platforms for deploying Flask applications.

#### Step 1: Prepare for Heroku

Create a `Procfile` in the project root:

```
web: gunicorn src.app:app
```

Create a `runtime.txt` file:

```
python-3.8.12
```

Update `requirements.txt` to include gunicorn:

```bash
pip install gunicorn
pip freeze > src/requirements.txt
```

#### Step 2: Create Heroku App

```bash
# Install Heroku CLI if not already installed
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create a new Heroku app
heroku create ai-influencer-generator

# Add buildpacks
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

#### Step 3: Configure Heroku Environment

```bash
heroku config:set SECRET_KEY=your_secret_key_here
heroku config:set MODEL_PATH=/app/models
heroku config:set DATA_PATH=/app/data
```

#### Step 4: Deploy to Heroku

```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

#### Step 5: Set Up Persistent Storage

Since Heroku's filesystem is ephemeral, you'll need to use add-ons for persistent storage:

```bash
# Add Heroku Postgres for database storage
heroku addons:create heroku-postgresql:hobby-dev

# For file storage, consider using AWS S3
heroku config:set AWS_ACCESS_KEY_ID=your_access_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret_key
heroku config:set S3_BUCKET_NAME=your_bucket_name
```

Update your application code to use S3 for file storage instead of local filesystem.

### AWS Deployment

AWS offers multiple options for deploying Flask applications. We'll cover Elastic Beanstalk, which provides a managed environment.

#### Step 1: Prepare for AWS Elastic Beanstalk

Install the EB CLI:

```bash
pip install awsebcli
```

Initialize EB application:

```bash
eb init -p python-3.8 ai-influencer-generator
```

Create a `.ebignore` file to exclude unnecessary files:

```
venv/
__pycache__/
*.pyc
instance/
.git/
.env
```

Create an `application.py` file in the project root that imports your Flask app:

```python
from src.app import app as application

if __name__ == "__main__":
    application.run()
```

#### Step 2: Configure AWS Environment

Create a `.ebextensions` directory and add configuration files:

```bash
mkdir -p .ebextensions
```

Create `.ebextensions/01_packages.config`:

```yaml
packages:
  yum:
    git: []
    gcc: []
    ffmpeg: []
```

Create `.ebextensions/02_python.config`:

```yaml
option_settings:
  "aws:elasticbeanstalk:container:python":
    WSGIPath: application.py
  "aws:elasticbeanstalk:application:environment":
    SECRET_KEY: "your_secret_key_here"
    MODEL_PATH: "/var/app/current/models"
    DATA_PATH: "/var/app/current/data"
```

#### Step 3: Create and Deploy to Elastic Beanstalk Environment

```bash
eb create ai-influencer-env
```

#### Step 4: Set Up Persistent Storage

Create an S3 bucket for file storage and update your application to use it.

For the database, you can use Amazon RDS:

```bash
# Create an RDS instance through the AWS console or CLI
# Then set the environment variables
eb setenv RDS_HOSTNAME=your-db-instance.rds.amazonaws.com
eb setenv RDS_PORT=5432
eb setenv RDS_DB_NAME=ebdb
eb setenv RDS_USERNAME=your_username
eb setenv RDS_PASSWORD=your_password
```

### Google Cloud Platform Deployment

GCP offers App Engine for deploying Flask applications with minimal configuration.

#### Step 1: Prepare for GCP App Engine

Install the Google Cloud SDK and initialize:

```bash
# Follow instructions at https://cloud.google.com/sdk/docs/install
gcloud init
```

Create an `app.yaml` file in the project root:

```yaml
runtime: python38

entrypoint: gunicorn -b :$PORT src.app:app

env_variables:
  SECRET_KEY: "your_secret_key_here"
  MODEL_PATH: "/tmp/models"
  DATA_PATH: "/tmp/data"

handlers:
- url: /static
  static_dir: src/static

- url: /.*
  script: auto
```

#### Step 2: Update Requirements

Ensure `gunicorn` is in your `requirements.txt`:

```bash
pip install gunicorn
pip freeze > src/requirements.txt
```

#### Step 3: Deploy to App Engine

```bash
gcloud app deploy
```

#### Step 4: Set Up Persistent Storage

For GCP, use Cloud Storage for file storage and Cloud SQL for database:

```bash
# Create a Cloud Storage bucket
gsutil mb gs://ai-influencer-storage

# Create a Cloud SQL instance through the GCP console or gcloud CLI
# Then update your application to use these resources
```

## Environment Configuration

### Production Settings

For production deployments, update the following settings:

1. Set `DEBUG = False` in your Flask application
2. Use a strong, randomly generated `SECRET_KEY`
3. Configure proper logging
4. Set up HTTPS with SSL certificates
5. Implement rate limiting and other security measures

Example production configuration:

```python
# config.py
import os
from datetime import timedelta

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # File paths
    MODEL_PATH = os.environ.get('MODEL_PATH', './models')
    DATA_PATH = os.environ.get('DATA_PATH', './data')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Security headers
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
```

### Environment-Specific Configuration

Create separate configuration files for different environments:

- `config/development.py`
- `config/production.py`
- `config/testing.py`

Load the appropriate configuration based on the environment:

```python
# app.py
import os
from flask import Flask

app = Flask(__name__)

if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')
```

## Database Setup

The MVP uses file-based storage with JSON metadata, but for production, consider using a proper database:

### SQLite (Simple Option)

```python
# In app.py
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

### PostgreSQL (Recommended for Production)

```python
# In app.py
from flask_sqlalchemy import SQLAlchemy

db_uri = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost/dbname')
# Heroku provides DATABASE_URL in the format postgres://, but SQLAlchemy requires postgresql://
if db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

### Database Migrations

Use Flask-Migrate to handle database schema changes:

```bash
pip install Flask-Migrate
```

```python
# In app.py
from flask_migrate import Migrate

migrate = Migrate(app, db)
```

Initialize and manage migrations:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Model Deployment

### Option 1: Include Models in Application

For smaller models, include them directly in your application:

```python
# In image_generator.py
import os
from diffusers import StableDiffusionPipeline

class ImageGenerator:
    def __init__(self):
        model_path = os.path.join(os.environ.get('MODEL_PATH', './models'), 'sdxl')
        self.pipeline = StableDiffusionPipeline.from_pretrained(model_path)
        # Move to GPU if available
        if torch.cuda.is_available():
            self.pipeline = self.pipeline.to("cuda")
```

### Option 2: Separate Model Server

For larger models or better scaling, use a separate model server:

1. Deploy models using TorchServe, TensorFlow Serving, or Triton Inference Server
2. Update your application to make API calls to the model server

Example with TorchServe:

```bash
# Create model archive
torch-model-archiver --model-name sdxl --version 1.0 --model-file model.py --serialized-file model.pth --export-path model_store

# Start TorchServe
torchserve --start --model-store model_store --models sdxl=sdxl.mar
```

Then update your application to call the model server:

```python
# In image_generator.py
import requests

class ImageGenerator:
    def __init__(self):
        self.model_server_url = os.environ.get('MODEL_SERVER_URL', 'http://localhost:8080')
    
    def generate_image(self, prompt, **kwargs):
        response = requests.post(
            f"{self.model_server_url}/predictions/sdxl",
            json={"prompt": prompt, **kwargs}
        )
        # Process response and return image
```

## Scaling Considerations

### Horizontal Scaling

For web tier scaling:
- Use a load balancer (e.g., Nginx, AWS ELB, GCP Load Balancing)
- Deploy multiple instances of your Flask application
- Ensure session management works across instances (use Redis or database-backed sessions)

Example Nginx configuration as a load balancer:

```nginx
http {
    upstream flask_app {
        server 127.0.0.1:5000;
        server 127.0.0.1:5001;
        server 127.0.0.1:5002;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Vertical Scaling

For compute-intensive operations:
- Use more powerful instances for model inference
- Consider GPU instances for faster image and video generation
- Optimize model loading and inference (quantization, batching)

### Asynchronous Processing

For long-running tasks:
- Implement a task queue system (Celery, RQ)
- Process image and video generation asynchronously
- Notify users when processing is complete

Example with Celery:

```bash
pip install celery redis
```

```python
# In celery_app.py
from celery import Celery

celery_app = Celery('ai_influencer',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

@celery_app.task
def generate_image_task(prompt, **kwargs):
    from models.image_generator import ImageGenerator
    generator = ImageGenerator()
    return generator.generate_image(prompt, **kwargs)
```

```python
# In your Flask routes
from celery_app import generate_image_task

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt')
    task = generate_image_task.delay(prompt)
    return jsonify({'task_id': task.id})

@app.route('/task-status/<task_id>')
def task_status(task_id):
    task = generate_image_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'status': 'pending'}
    elif task.state == 'SUCCESS':
        response = {'status': 'success', 'result': task.result}
    else:
        response = {'status': 'failure', 'error': str(task.result)}
    return jsonify(response)
```

## Monitoring and Maintenance

### Logging

Set up comprehensive logging:

```python
# In app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AI Influencer Generator startup')
```

### Health Checks

Implement health check endpoints:

```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

### Monitoring Tools

Set up monitoring with:
- Prometheus for metrics collection
- Grafana for visualization
- Sentry for error tracking

Example Prometheus integration:

```bash
pip install prometheus-flask-exporter
```

```python
# In app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

### Backup Strategy

Implement regular backups:
- Database backups (daily)
- File storage backups (daily)
- Configuration backups (after changes)

Example backup script:

```bash
#!/bin/bash
# backup.sh

# Backup database
pg_dump -U username -d dbname > backups/db_$(date +%Y%m%d).sql

# Backup files
tar -czf backups/files_$(date +%Y%m%d).tar.gz data/

# Rotate backups (keep last 7 days)
find backups/ -name "*.sql" -mtime +7 -delete
find backups/ -name "*.tar.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

- Check for syntax errors in Python files
- Verify all dependencies are installed
- Ensure environment variables are set correctly
- Check port availability

#### Model Loading Errors

- Verify model files exist in the correct location
- Check for sufficient disk space
- Ensure GPU drivers are installed if using GPU acceleration

#### Slow Performance

- Monitor resource usage (CPU, memory, disk I/O)
- Consider scaling up or out
- Optimize database queries
- Implement caching for frequently accessed data

#### File Storage Issues

- Check disk space and permissions
- Verify path configurations
- Consider using object storage for scalability

### Debugging Tools

- Use Flask's debug mode during development
- Implement detailed logging
- Use profiling tools to identify bottlenecks

```python
# Example profiling middleware
from werkzeug.middleware.profiler import ProfilerMiddleware

if app.config['DEBUG']:
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
```

## Conclusion

This deployment guide covers the essential steps for deploying the AI Influencer Content Generator in both local and cloud environments. By following these instructions, you can set up a scalable, maintainable, and production-ready application.

For specific issues or advanced configurations, refer to the documentation of the respective tools and platforms or contact the development team for support.

Remember to regularly update dependencies, apply security patches, and monitor the application's performance to ensure optimal operation.
