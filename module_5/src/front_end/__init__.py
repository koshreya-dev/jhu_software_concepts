"""Flask application factory for the front end."""


def create_app():
    """
    Create and configure a new Flask application instance.

    This function dynamically imports and returns the existing app instance
    to ensure all routes are properly registered within the application context.
    """
    # Import the app here to avoid circular import errors.
    from .app import app  # pylint: disable=C0415
    return app
