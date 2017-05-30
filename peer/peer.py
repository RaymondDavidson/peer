# -*- coding: utf-8 -*-
""" Routes for essay analysis interface"""

import os

from werkzeug.utils import secure_filename

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from input import read_document
import werkzeug


UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['txt', 'docx', 'pdf', 'odt'])
topbar = Navbar('',
    Text('Extra Eyes'),
    View('About', 'about'),
    View('Home', 'intro'),
    View('Upload', 'upload_file'),
    View('Usage', 'usage'),
    Link('Style Checks','http://proselint.com/checks/'),
    Subgroup('Resources',
             Link('Lard', 'http://proftgreene.pbworks.com/w/file/fetch/50167777/Richard%20Lanhams%20Paramedic%20Method%20of%20Revision.pdf'),
             Link('Readability', 'http://www.analyzemywriting.com/readability_indices.html'),
             Link('Revision Strategies', 'http://greyfiti.wikidot.com/sdg:gmeth-ref-guidelines-substantive-revision')
             ),
)

nav = Nav()
nav.register_element('top', topbar)
app = Flask(__name__)
Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEBUG'] = True
nav.init_app(app)






def allowed_file(filename):
    """Make sure filetype has allowed extension."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def intro():
    """Flask route to index with explanatory contant."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Flask route to explanatory contant."""
    return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
    Upload file to UPLOAD_FOLDER from form on upload template.

    Return:
        Redirect to feedback template on successful POST.
    """
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
    """Route to analysis results (of uploaded file)"""
    os.remove(Doc.path)
    return render_template('results.html', object=Doc)

@app.route('/content')
def content():
    return render_template('content.html', object=Doc)

@app.route('/usage')
def usage():
    return render_template('usage.html')

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    return render_template('internal.html'), 500

if __name__ == "__main__":
    app.run()
