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


@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    GET /api/health
    Health check endpoint returning system status.
    """
    return jsonify({
        'status': 'healthy',
        'application': 'HintSpark AI Math Helper',
        'version': '2.0.0'
    })


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
        
        # Safely reload dotenv with dotenv_path parameter
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path, override=True)
        except Exception as err:
            print(f"Dotenv reload note: {err}")

        return jsonify({
            'status': 'success',
            'message': f'Successfully updated {env_var_name} in .env file!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to save .env file: {str(e)}'
        }), 500


@main_bp.route('/api/clear_key', methods=['POST'])
def clear_key():
    """
    POST /api/clear_key
    Industry Standard Clear: Removes API keys from local .env file on disk 
    and unsets them from Python in-memory os.environ.
    """
    try:
        env_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        
        # Unset from in-memory environment
        for key in ["GEMINI_API_KEY", "CLAUDE_API_KEY", "API"]:
            os.environ.pop(key, None)

        # Clear key values in .env file on disk
        if os.path.exists(env_path):
            env_lines = []
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY=") or line.startswith("CLAUDE_API_KEY=") or line.startswith("API="):
                        var_name = line.split('=')[0]
                        env_lines.append(f'{var_name}=""\n')
                    else:
                        env_lines.append(line)
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_lines)

            # Reload dotenv with override=True
            try:
                from dotenv import load_dotenv
                load_dotenv(dotenv_path=env_path, override=True)
            except Exception as err:
                print(f"Dotenv clear reload note: {err}")

        return jsonify({
            'status': 'success',
            'message': 'Successfully cleared API keys from browser and server .env file!'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to clear .env file: {str(e)}'
        }), 500
