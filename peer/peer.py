# -*- coding: utf-8 -*-
""" Routes for essay analysis interface"""
import os

from werkzeug.utils import secure_filename

from flask import Flask, flash, redirect, render_template, request, url_for, session, make_response
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from input import read_document
from input import read_text
import werkzeug
# import time

"""
Upload Folder

Defined differently for difference scenarios:

* pythonanywhere
* wsgi
* flask dev
"""

UPLOAD_FOLDER = 'tmp' # local dev
# UPLOAD_FOLDER = '/tmp' # pythonanywhere
# UPLOAD_FOLDER = '/var/www/peer/peer/tmp' # wsgi

ALLOWED_EXTENSIONS = set(['txt', 'docx', 'odt'])
topbar = Navbar('',
    Text('Extra Eyes'),
    View('About', 'about'),
    View('Home', 'intro'),
    #View('Upload', 'upload_file'),
    #View('Paste Text', 'paste'),
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
app.secret_key = 'riverrun, past Eve and Adam’s, from swerve of shore to \
    bend of bay, brings us by a commodius vicus of recirculation back to \
    Howth Castle and Environs.'
#app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_TYPE'] = 'null'
app.config['SESSION_PERMANENT'] = 'False'
Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

nav.init_app(app)

_samples=[]


def allowed_file(filename):
    """
    Make sure filetype has allowed extension.

    * docx: most reliable
    * odt: through textract (spaces between words disappear, as do
        apostrophes)
    * txt: works fine
    """

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/clear')
def clearRawText():
    del Doc.raw_text
    del Doc.file_name
    del Doc.intro
    del Doc.exit
    del Doc.passive_sentences
    del Doc.comma_example
    del Doc.cliche_list

    return redirect(url_for('intro'))

"""
def clearSession(instance=Doc):
    '''
    Stop intermittant breaking between upload and parsing, delivering instance.

    Still not clear if this is the remedy.
    '''



    try:
        session.clear()
        print "Session cleared"
    except:
        print "Attempt to clear session failed"
        pass


    try:
        deleteInstance(instance)
        del instance
    except:
        pass

    if Doc:
        print "The instance of Sample has not been properly destroyed."
    else:
        print "There is not Sample instance called 'Doc'"

    return redirect(url_for('intro'))
"""


@app.route('/')
def intro():
    """ Flask route to index with explanatory content. """
    """
    try:
        session.clear()
    except:
        print "couldn't clear session"
        pass
    """
    return render_template('index.html')

@app.route('/about')
def about():
    """Flask route to the about page."""
    return render_template('about.html')


@app.route('/paste', methods=['GET', 'POST'])
def paste():
    if request.method == 'POST':
        result = request.form
        if 'submission' not in result:
            flash('No text submitted') # does not work yet
            return redirect(request.url)
        prose = result['submission']
        global Doc
        Doc = read_document.Sample(prose)
        #time.sleep(3) # doesn't resolve intemittant breaking
        return redirect(url_for('paste_results', object=Doc))
    return render_template('paste.html')

"""
# this was a temporary test.
@app.route('/paste_contents', methods=['GET', 'POST'])
def paste_contents():
    if request.method == 'POST':
        result = request.form
        return render_template("paste_results.html", result=result)
"""

@app.route('/paste_results', methods=['GET', 'POST'])
def paste_results():
    """
    Return analysis results -- of pasted text).

    Note that this looks like a GET method instead of POST method.

    .. todo:: stop showing instance address in url

    """
    return render_template('paste_results.html', object=Doc)

@app.route('/paste_full')
def paste_full():
    """ Show full text of the pasted content."""
    return render_template('paste_text.html', object=Doc)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
    Upload file to UPLOAD_FOLDER from form on upload template.

    After upload, create instance, then redirect to results.

    .. todo::
        * add some kind of indicator that the wait is expected
        * make flash work

    Return:
        Redirect to feedback template on successful POST.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part') # does not work yet
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file') # does not work
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            global Doc
            #time.sleep(3) # no effect on intermittent instance creation
            Doc = read_document.Sample(UPLOAD_FOLDER + "/" + filename)
            return redirect(url_for('feedback', timestamp=Doc.time_stamp))
    return render_template('upload.html')

@app.route('/feedback/<timestamp>', methods=['GET', 'POST'])
def feedback(timestamp):
    """
    Route to analysis results (of uploaded file)

    On the way, remove the uploaded doc from the defined storage location
    """
    try:
        if Doc:
            print "An instance of Sample exists."
    except:
        print("No instance.")
    try:
        if Doc.raw_text:
            _samples.append(timestamp)
            for sample in _samples:
                print sample
            try:
                if os.path.isfile(Doc.abs_path):
                    os.remove(Doc.abs_path)
                if not os.path.isfile(Doc.abs_path):
                    print "Destroyed tmp file %s." % Doc.abs_path
            except:
                print "Failed to remove tmp file %s. Please check owner and \
                    permissions" % Doc.abs_path
                pass
            return render_template('results.html', object=Doc)
    except:
        return render_template('404.html')


"""
def deleteInstance(instance):
    '''
    Delete the Sample instance.

    Part of work to identify the cause of the inconsistent success creating
    and displaying the results (instance).
    '''
    try:
        if instance:
            del Doc
        else:
            print "There is not Sample instance called %" % instance
    except:
        if instance:
            print "Could not delete instance %s. \
                    It may not have existed." % instance
        pass
"""




@app.route('/content')
def content():
    """
    Show full text of the raw_text of the instance from upload.

    (object.raw_text)
    """
    return render_template('content.html', object=Doc)

@app.route('/usage')
def usage():
    """ Show documentation. """
    return render_template('usage.html')

@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    """ Error handler that appears to be working """
    return render_template('internal.html'), 500


@app.route('/404')
def page_not_found():
    return render_template('404.html')


if __name__ == "__main__":
    app.run()
