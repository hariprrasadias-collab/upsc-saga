from wsgi import app

# This file exists to support Render Start Commands that might be hardcoded to `gunicorn app:app`.
# The main entry point is `wsgi.py`, but this ensures backward compatibility.
if __name__ == '__main__':
    app.run(debug=True, port=5000)
