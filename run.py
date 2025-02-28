"""
Application entry point for the Voice Assistant system.
Starts the Flask server with the appropriate host and debug settings.
This file is used to launch the application in a development environment.
"""
from app import create_app


flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True)