from flask import Flask, render_template, request, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
app.secret_key = 'harikrishnan4607'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload and static folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "grayScale":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "webp": 
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "jpg": 
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "png": 
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
    pass

def resizeImage(filename, width,height):
    img = cv2.imread(f"uploads/{filename}")
    (h, w) = img.shape[:2]
    new_width = int(width)
    aspect_ratio = int(h / w)
    new_height = new_width*aspect_ratio
    resized_img = cv2.resize(img, (new_width, new_height))
    newFilename = f"static/{filename.split('.')[0]}_resized.jpg"
    cv2.imwrite(newFilename, resized_img)
    return newFilename

def editImage(filename,operation):
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "rotate90":
            imgProcessed = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "denoise":
            imgProcessed = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 15)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "bilateral":
            imgProcessed = cv2.bilateralFilter(img, 5, 50, 50)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "histogram":
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgProcessed = cv2.equalizeHist(gray_img)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed) 
            return newFilename
        case "avgFilter":
            imgProcessed = cv2.blur(img, (5, 5))
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "median":
            imgProcessed = cv2.medianBlur(img, 5)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename

            



@app.route('/image-converter')
def convert():
    return render_template('image-converter.html')

@app.route('/image-resize')
def resize():
    return render_template('image-resizer.html')

@app.route('/image-editor')
def editor():
    return render_template('image-editor.html')

@app.route('/insert', methods=["GET","POST"])
def insert():
    if request.method == 'POST':
        operation = request.form.get("operation")
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template("image-converter.html")
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template("image-converter.html")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/download/{new}' target='_blank'>here</a>")
            return render_template("image-converter.html")
        else:
            flash('File not allowed')
            return render_template("image-converter.html")
    return render_template("image-converter.html")

@app.route('/insert-resize', methods=["GET","POST"])
def insertResize():
    if request.method == 'POST':
        width = request.form.get("width")
        height = request.form.get("height")
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template("image-resizer.html")
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template("image-resizer.html")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = resizeImage(filename, width,height)
            flash(f"Your image has been processed and is available <a href='/download/{new}' target='_blank'>here</a>")
            return render_template("image-resizer.html")
        else:
            flash('File not allowed')
            return render_template("image-resizer.html")
    return render_template("image-resizer.html")

@app.route('/insert-edit', methods=["GET","POST"])
def insertEdit():
    if request.method == 'POST':
        operation=request.form.get('operation')

        
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template("image-editor.html")
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template("image-editor.html")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = editImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/download/{new}' target='_blank'>here</a>")
            return render_template("image-editor.html")
        else:
            flash('File not allowed')
            return render_template("image-editor.html")
    return render_template("image-editor.html")


@app.route('/download/static/<filename>')
def download_file(filename):
    return send_from_directory(STATIC_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=7001)