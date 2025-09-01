# Create Flask app using blueprint

from flask import Flask

from module_1 import pages

def create_app():
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app