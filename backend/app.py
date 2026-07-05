"""
app.py  –  Flask entry point for Song Recommender
"""

from flask import Flask
from flask_cors import CORS
from routes.predict import predict_bp
from routes.recommend import recommend_bp
from routes.dashboard import dashboard_bp

def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )
    app.config["SECRET_KEY"] = "song-recommender-secret-2024"
    CORS(app)

    # register blueprints
    app.register_blueprint(predict_bp,   url_prefix="/api")
    app.register_blueprint(recommend_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")

    # serve frontend
    from flask import render_template
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/predict")
    def predict_page():
        return render_template("predict.html")

    @app.route("/recommend")
    def recommend_page():
        return render_template("recommend.html")

    @app.route("/dashboard")
    def dashboard_page():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
