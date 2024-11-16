import sys
import os

# Add the absolute path of the parent directory of `myapp` to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from myapp import app, db

with app.app_context():
    db.create_all()
