"""
HintSpark — REST API & AI Tutor Routes
======================================
Serves REST API endpoints for blog management and real-time AI tutor interactions.
"""

from flask import Blueprint, request, jsonify
from services.blog_service import get_filtered_blogs, create_new_blog
from services.ai_service import get_tutor_hint

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/blogs', methods=['GET'])
def get_blogs():
    """
    GET /api/blogs
    Fetch list of math blog posts with optional category filter and keyword search.
    """
    try:
        category = request.args.get('category', 'All')
        search = request.args.get('search', '')
        blogs = get_filtered_blogs(category, search)
        return jsonify({
            'status': 'success',
            'count': len(blogs),
            'blogs': blogs
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/api/blogs', methods=['POST'])
def add_blog():
    """
    POST /api/blogs
    Create and store a new math article.
    """
    try:
        data = request.json or {}
        new_blog = create_new_blog(data)
        return jsonify({'status': 'success', 'blog': new_blog}), 201
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/get_hint', methods=['POST'])
def get_hint():
    """
    POST /get_hint
    Generate a guided hint for a math problem using Gemini API or Anthropic Claude API.
    """
    try:
        data = request.json or {}
        user_input = data.get('prompt', '')
        client_key = request.headers.get('X-Gemini-API-Key') or data.get('api_key', '')

        response_text = get_tutor_hint(user_input, client_key)
        return jsonify({
            'status': 'success',
            'response': response_text
        })
    except ValueError as ve:
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
