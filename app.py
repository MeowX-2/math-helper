"""
HintSpark — Math Insights & AI Assistant Application Entry
===========================================================
Modular Flask application initializing blueprints, global error handlers,
and WSGI entry point for local and production deployment.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Application factory for modular Flask application setup."""
    app = Flask(__name__)

    # Register Route Blueprints
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith('/api/') or request.path == '/get_hint':
            return jsonify({'status': 'error', 'message': 'Requested API endpoint not found.'}), 404
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def handle_500(e):
        print(f"Global 500 Error: {e}")
        if request.path.startswith('/api/') or request.path == '/get_hint':
            return jsonify({'status': 'error', 'message': 'Internal Server Error. Please check backend logs.'}), 500
        return render_template('index.html'), 500

    return app

# WSGI Application instance for Gunicorn / Render / Heroku
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
