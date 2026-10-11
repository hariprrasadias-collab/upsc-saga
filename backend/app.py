import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # During render build phase, PORT is injected. We only start the dev server
    # if it's explicitly run. In production, gunicorn should be used.
    if os.environ.get('NODE_ENV') != 'production' and not os.environ.get('RENDER'):
        app.run(host='0.0.0.0', debug=True, port=int(os.environ.get("PORT", 5000)))
