import sys
import logging
logging.basicConfig(stream=sys.stderr)

# add your project directory to the sys.path
project_home = u'/var/www/peer/peer'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from peer import app as application
