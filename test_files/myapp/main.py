import sys
import os

# Add the parent directory of `myapp` to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from myapp import app

if __name__ == '__main__':
    app.run(debug=True)
