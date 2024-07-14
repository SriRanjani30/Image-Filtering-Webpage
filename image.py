from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PIL import Image, ImageFilter, ImageOps
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def apply_grayscale(image):
    return ImageOps.grayscale(image)

def apply_sepia(image):
    width, height = image.size
    pixels = image.load()  # Create the pixel map

    for py in range(height):
        for px in range(width):
            r, g, b = image.getpixel((px, py))

            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)

            # Normalize if out of bounds
            if tr > 255:
                tr = 255
            if tg > 255:
                tg = 255
            if tb > 255:
                tb = 255

            pixels[px, py] = (tr, tg, tb)

    return image

def apply_blur(image, radius=5):
    return image.filter(ImageFilter.GaussianBlur(radius))

def apply_edge_detection(image):
    return image.filter(ImageFilter.FIND_EDGES)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('show_filters', filename=file.filename))

@app.route('/filters/<filename>')
def show_filters(filename):
    return render_template('filters.html', filename=filename)

@app.route('/apply_filter/<filename>/<filter_name>')
def apply_filter(filename, filter_name):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(filepath)
    
    if filter_name == 'grayscale':
        filtered_image = apply_grayscale(image)
    elif filter_name == 'sepia':
        filtered_image = apply_sepia(image)
    elif filter_name == 'blur':
        filtered_image = apply_blur(image)
    elif filter_name == 'edge_detection':
        filtered_image = apply_edge_detection(image)
    
    output_filename = f"{filter_name}_{filename}"
    output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    filtered_image.save(output_filepath)
    
    return send_from_directory(app.config['OUTPUT_FOLDER'], output_filename)

if __name__ == '__main__':
    app.run(debug=True)
