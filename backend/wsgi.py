import sys
import os

# Ensure the current directory is in sys.path so 'app' package is resolvable
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
