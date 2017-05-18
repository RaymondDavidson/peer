""" Routes for essay analysis interface"""

import os
from flask import Flask, request, redirect, url_for, flash, render_template
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from input import read_document

UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['txt', 'docx', 'doc', 'pdf', 'odt'])

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEBUG'] = True

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def intro():
    # Should be explanatory content, examples, navigation
    return 'Welcome. Click <a href="/upload">here</a> to upload.'



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
            global Doc
            Doc = read_document.Sample(UPLOAD_FOLDER + "/" + filename)
            return redirect(url_for('feedback'))

    return render_template('upload.html')

@app.route('/feedback')
def feedback():
    print Doc.ptext
    return render_template('results.html', object=Doc)
