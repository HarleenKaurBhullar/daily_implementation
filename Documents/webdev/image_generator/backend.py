from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
from PIL import Image
from io import BytesIO
import time
from datetime import datetime
import mimetypes

# Load environment variables from global .env file
# Your .env is at: ~/.env (home directory)
# Your backend is at: ~/Documents/webdev/image_generator/
env_path = os.path.expanduser('~/.env')
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API setup
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {os.getenv('HuggingFace_API_Key')}"}

# Create images directory if it doesn't exist
images_dir = os.path.join(os.path.dirname(__file__), 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    print(f"Created images directory at: {images_dir}")
else:
    print(f"Images directory exists at: {images_dir}")

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}.png"
        filepath = os.path.join(images_dir, filename)
        
        print(f"Generating image for prompt: {prompt}")
        print(f"Will save image to: {filepath}")
        
        # Generate image
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "options": {"wait_for_model": True}
        })
        
        if response.status_code == 200:
            # Save image
            image = Image.open(BytesIO(response.content))
            image.save(filepath)
            
            print(f"Image saved to: {filepath}")
            
            # Return success response
            return jsonify({
                'success': True,
                'image_url': f'/images/{filename}',
                'image_path': filepath,
                'message': 'Image generated successfully'
            })
            
        elif response.status_code == 503:
            print("Model is loading, retrying in 20 seconds...")
            # Model is loading, retry once
            time.sleep(20)
            response = requests.post(API_URL, headers=headers, json={
                "inputs": prompt,
                "options": {"wait_for_model": True}
            })
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.save(filepath)
                print(f"Image saved to: {filepath} (after retry)")
                return jsonify({
                    'success': True,
                    'image_url': f'/images/{filename}',
                    'image_path': filepath,
                    'message': 'Image generated successfully (after retry)'
                })
            else:
                print(f"Error after retry: {response.status_code}")
                return jsonify({
                    'success': False,
                    'error': f'Error after retry: {response.status_code}'
                }), 500
        else:
            print(f"API Error: {response.status_code}")
            return jsonify({
                'success': False,
                'error': f'API Error: {response.status_code}'
            }), 500
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from the images directory"""
    try:
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        print(f"Looking for image at: {os.path.join(images_dir, filename)}")
        print(f"Images directory exists: {os.path.exists(images_dir)}")
        print(f"File exists: {os.path.exists(os.path.join(images_dir, filename))}")
        
        if os.path.exists(os.path.join(images_dir, filename)):
            return send_from_directory(images_dir, filename)
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        print(f"Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

@app.route('/style.css')
def serve_css():
    """Serve CSS file"""
    try:
        return send_from_directory('.', 'style.css')
    except Exception as e:
        print(f"Error serving CSS: {str(e)}")
        return "/* CSS file not found */", 404

@app.route('/script.js')
def serve_js():
    """Serve JavaScript file"""
    try:
        return send_from_directory('.', 'script.js')
    except Exception as e:
        print(f"Error serving JS: {str(e)}")
        return "// JavaScript file not found", 404

@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        print(f"Error serving index.html: {str(e)}")
        return "HTML file not found", 404

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'AI Image Generator API is running',
        'timestamp': datetime.now().isoformat()
    })

# List generated images endpoint
@app.route('/images')
def list_images():
    """List all generated images"""
    try:
        images = []
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    filepath = os.path.join(images_dir, filename)
                    stat = os.stat(filepath)
                    images.append({
                        'filename': filename,
                        'url': f'/images/{filename}',
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        return jsonify({
            'success': True,
            'images': sorted(images, key=lambda x: x['created'], reverse=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting AI Image Generator Server...")
    print("Server will be available at: http://localhost:5000")
    print("Health check available at: http://localhost:5000/health")
    print("Images list available at: http://localhost:5000/images")
    
    # Debug: Check if .env file is loaded
    api_key = os.getenv('HuggingFace_API_Key')
    if api_key:
        print("✓ Environment variables loaded successfully")
    else:
        print("✗ Warning: HuggingFace_API_Key not found in environment variables")
        print(f"✗ Looking for .env file at: {os.path.abspath(env_path)}")
    
    app.run(debug=True, port=5000, host='0.0.0.0')