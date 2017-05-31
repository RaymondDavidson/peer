# -*- coding: utf-8 -*-
""" Routes for essay analysis interface"""
import os

from werkzeug.utils import secure_filename

from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from input import read_document
from input import read_text
import werkzeug


UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['txt', 'docx', 'pdf', 'odt'])
topbar = Navbar('',
    Text('Extra Eyes'),
    View('About', 'about'),
    View('Home', 'intro'),
    View('Upload', 'upload_file'),
    View('Paste Text', 'paste'),
    View('Usage', 'usage'),
    Link('Style Checks','http://proselint.com/checks/'),
    Subgroup('Resources',
             Link('Lard', 'http://proftgreene.pbworks.com/w/file/fetch/50167777/Richard%20Lan    hams%20Paramedic%20Method%20of%20Revision.pdf'),
             Link('Readability',
                  'http://www.analyzemywriting.com/readability_indices.html'),
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


@app.route('/paste', methods=['GET', 'POST'])
def paste():
    if request.method == 'POST':
        result = request.form
        if 'submission' not in result:
            flash('No text submitted')
            return redirect(request.url)
        prose = result['submission']
        global Sample
        Sample = read_text.TextSample(prose)
        return redirect(url_for('paste_results', object=Sample))
    return render_template('paste.html')

# temporary - testing only
@app.route('/paste_contents', methods=['GET', 'POST'])
def paste_contents():
    if request.method == 'POST':
        result = request.form
        return render_template("paste_results.html", result=result)

@app.route('/paste_results', methods=['GET', 'POST'])
def paste_results():
    """Route to analysis results (of pasted text)"""
    return render_template('paste_results.html', object=Sample)

@app.route('/paste_full')
def paste_full():
    return render_template('paste_text.html', object=Sample)

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

app.secret_key = 'riverrun'
#app.config['SESSION_TYPE'] = 'filesystem'


if __name__ == "__main__":
    #app.run()

    app.run()
