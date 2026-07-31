"""
HintSpark — Main Web Routes & System API
==========================================
Serves web application shell HTML and environment configuration endpoints.
"""

import os
from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render main web page application shell."""
    return render_template('index.html')


@main_bp.route('/api/check_key', methods=['GET'])
def check_key():
    """
    GET /api/check_key
    Check if a Gemini or Claude API key is configured on the server environment.
    """
    current_key = os.getenv("GEMINI_API_KEY") or os.getenv("CLAUDE_API_KEY") or os.getenv("API")
    return jsonify({
        'status': 'success',
        'has_key': bool(current_key and current_key.strip())
    })


@main_bp.route('/api/save_env', methods=['POST'])
def save_env():
    """
    POST /api/save_env
    Dynamically save or update user API Key in local .env file.
    """
    try:
        data = request.json or {}
        api_key = data.get('api_key', '').strip()

        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API Key cannot be empty.'
            }), 400

        # Clean quotes
        clean_key = api_key.strip('"').strip("'")
        
        # Detect key type
        if clean_key.startswith('sk-ant-') or clean_key.startswith('sk-'):
            env_var_name = "CLAUDE_API_KEY"
        else:
            env_var_name = "GEMINI_API_KEY"

        env_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        
        env_lines = []
        key_updated = False
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith(f"{env_var_name}="):
                        env_lines.append(f'{env_var_name}="{clean_key}"\n')
                        key_updated = True
                    else:
                        env_lines.append(line)

        if not key_updated:
            env_lines.append(f'{env_var_name}="{clean_key}"\n')

        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_lines)

        os.environ[env_var_name] = clean_key

        return jsonify({
            'status': 'success',
            'message': f'Successfully updated {env_var_name} in .env file!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to save .env file: {str(e)}'
        }), 500
