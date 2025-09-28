"""Factory to create and configure the Flask application for tests."""
from flask import Flask, jsonify, render_template

def create_app(pool=None, scraper=None):
    """
    Create and configure the Flask application.

    This factory function is used for creating a Flask application instance
    that can be configured with different mock services for testing.
    """
    new_app = Flask(__name__)
    new_app.config["POOL"] = pool
    new_app.config["SCRAPER"] = scraper
    new_app.SCRAPING_IN_PROGRESS = False

    @new_app.route("/analysis")
    def analysis():
        """Render the main analysis page."""
        return render_template("index.html")

    @new_app.route("/pull-data", methods=["POST"])
    def pull_data():
        """Initiate the data scraping process."""
        if new_app.SCRAPING_IN_PROGRESS:
            return jsonify({"busy": True}), 409
        new_app.SCRAPING_IN_PROGRESS = True
        rows = scraper()
        pool.insert_rows(rows)
        new_app.SCRAPING_IN_PROGRESS = False
        return jsonify({"ok": True}), 200

    @new_app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        """Update the data analysis."""
        if new_app.SCRAPING_IN_PROGRESS:
            return jsonify({"busy": True}), 409
        return jsonify({"ok": True}), 200

    return new_app
