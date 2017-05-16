# A very simple Flask Hello World app for you to get started with...
import os
from flask import Flask, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
# from input import read_document

UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['txt', 'docx', 'doc', 'pdf', 'odt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():
    # Should be explanatory content, examples, navigation
    return 'Hello from Flask! Click <a href="/upload">here</a> to upload.'

@app.route('/feedback')
def feedback():
    # redirect to analysis results
    # Doc = read_document.Sample(file)
    return "Here's your feedback."

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('feedback',
            #    filename=filename))
            return redirect(url_for('feedback'))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
