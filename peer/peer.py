""" Routes for essay analysis interface"""

import os
from flask import Flask, request, redirect, url_for, flash, render_template
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from input import read_document
from flask_nav import Nav
#from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_nav.elements import *



UPLOAD_FOLDER = 'tmp'
# ALLOWED_EXTENSIONS = set(['txt', 'docx', 'doc', 'pdf', 'odt'])
ALLOWED_EXTENSIONS = set(['txt', 'docx', 'pdf', 'odt'])
topbar = Navbar('',
    View('Home', 'intro'),
    View('Upload', 'upload_file'),
    View('Usage', 'usage'),
)

nav = Nav()
nav.register_element('top', topbar)
app = Flask(__name__)
Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEBUG'] = True
nav.init_app(app)







def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def intro():
    # Should be explanatory content, examples, navigation
    return render_template('index.html')



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
    os.remove(Doc.path)
    return render_template('results.html', object=Doc)

@app.route('/content')
def content():
    return render_template('content.html', object=Doc)

@app.route('/usage')
def usage():
    return render_template('usage.html')

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500
