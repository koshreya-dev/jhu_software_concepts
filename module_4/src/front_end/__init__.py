from .app import app  # import the existing Flask app

def create_app():
    # Import app here to ensure all route decorators are registered
    from .app import app
    return app