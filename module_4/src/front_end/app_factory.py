# Wrapper to expose the existing app as a factory for tests
from .app import app 

from flask import Flask, jsonify, render_template

def create_app(pool=None, scraper=None):
    app = Flask(__name__)
    app.config["POOL"] = pool
    app.config["SCRAPER"] = scraper
    app.SCRAPING_IN_PROGRESS = False

    @app.route("/analysis")
    def analysis():
        return render_template("index.html")

    @app.route("/pull-data", methods=["POST"])
    def pull_data():
        if app.SCRAPING_IN_PROGRESS:
            return jsonify({"busy": True}), 409
        app.SCRAPING_IN_PROGRESS = True
        rows = scraper()
        pool.insert_rows(rows)
        app.SCRAPING_IN_PROGRESS = False
        return jsonify({"ok": True}), 200

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        if app.SCRAPING_IN_PROGRESS:
            return jsonify({"busy": True}), 409
        # analysis logic here
        return jsonify({"ok": True}), 200

    return app
