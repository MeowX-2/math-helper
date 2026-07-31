"""
HintSpark — Math Insights & AI Assistant Backend
=================================================
Flask web application serving mathematical stories, articles, and an interactive 
AI tutor powered by the Google Gemini API.
"""

import os
import json
import time
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from google.generativeai.types import generation_types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure the Google Gemini API key if present
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API")
if api_key:
    genai.configure(api_key=api_key)

# Path to local JSON storage for blog posts
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'blogs.json')


# ==============================================================================
# Helper Functions: Data Storage & Math Read-Time Calculation
# ==============================================================================

def load_blogs():
    """
    Load blog entries from local JSON storage file.
    Returns an empty list if the file does not exist or fails to parse.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading blogs data: {e}")
        return []


def save_blogs(blogs):
    """
    Save list of blog objects into local JSON storage file.
    Automatically creates the parent directory if missing.
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(blogs, f, indent=2)


def calculate_read_time(content):
    """
    Calculate estimated reading time based on word count and inline/display LaTeX math blocks.
    """
    if not content:
        return "1 min read"
        
    words = len(content.split())
    
    # Estimate LaTeX complexity
    display_math = content.count('$$') // 2
    raw_dollars = content.count('$') - (display_math * 4)
    inline_math = max(0, raw_dollars // 2)

    total_seconds = (words / 150.0 * 60) + (inline_math * 15) + (display_math * 30)
    minutes = max(1, math.ceil(total_seconds / 60))
    return f"{minutes} min read"


# ==============================================================================
# Web Routes & REST API Endpoints
# ==============================================================================

@app.route('/')
def index():
    """Render main web page application shell."""
    return render_template('index.html')


@app.route('/api/check_key', methods=['GET'])
def check_key():
    """
    GET /api/check_key
    Check if a Gemini API key is currently configured on the server environment.
    """
    current_key = os.getenv("GEMINI_API_KEY") or os.getenv("API")
    return jsonify({
        'status': 'success',
        'has_key': bool(current_key and current_key.strip())
    })


@app.route('/api/save_env', methods=['POST'])
def save_env():
    """
    POST /api/save_env
    Save user-provided Gemini API key to local .env file on disk and initialize Gemini AI.
    Normalizes quote handling so whether input is 'a' or '"a"', it is stored as GEMINI_API_KEY="a".
    """
    try:
        data = request.json or {}
        raw_key = (data.get('api_key', '') or '').strip()
        
        # Clean all surrounding single and double quotes
        clean_key = raw_key.strip('"').strip("'").strip()

        if not clean_key:
            return jsonify({
                'status': 'error',
                'message': 'API Key cannot be empty.'
            }), 400

        # Path to .env file in project root
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Always store in clean format GEMINI_API_KEY="clean_key"
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f'# HintSpark Environment Configuration\nGEMINI_API_KEY="{clean_key}"\n')

        # Reload environment variables
        load_dotenv(env_path=env_path, override=True)
        
        # Reconfigure genai library with clean key
        genai.configure(api_key=clean_key)

        return jsonify({
            'status': 'success',
            'message': '.env file created and API key configured successfully!'
        })

    except Exception as e:
        print(f"Error writing .env file: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to write .env file: {str(e)}'
        }), 500


@app.route('/api/blogs', methods=['GET'])
def get_blogs():
    """
    GET /api/blogs
    Fetch articles filtered by category and search keyword, sorted by date descending.
    """
    category = request.args.get('category', 'All').strip()
    search = request.args.get('search', '').strip().lower()
    
    blogs = load_blogs()

    # Filter by category if specified
    if category and category != 'All':
        blogs = [b for b in blogs if b.get('category', '').lower() == category.lower()]
        
    # Filter by search string if provided
    if search:
        blogs = [
            b for b in blogs
            if search in b.get('title', '').lower()
            or search in b.get('subtitle', '').lower()
            or search in b.get('content', '').lower()
            or search in b.get('author', '').lower()
            or any(search in tag.lower() for tag in b.get('tags', []))
        ]

    # Return sorted by ID/Timestamp descending
    blogs.sort(key=lambda x: x.get('id', '0'), reverse=True)
    return jsonify({'status': 'success', 'blogs': blogs})


@app.route('/api/blogs', methods=['POST'])
def create_blog():
    """
    POST /api/blogs
    Publish a new article post.
    """
    try:
        data = request.json or {}
        title = data.get('title', '').strip()
        subtitle = data.get('subtitle', '').strip()
        author = data.get('author', '').strip() or 'Anonymous Math Writer'
        category = data.get('category', 'General').strip()
        tags_raw = data.get('tags', [])
        content = data.get('content', '').strip()

        if not title or not content:
            return jsonify({'status': 'error', 'message': 'Title and content are required.'}), 400

        # Parse tags input format
        if isinstance(tags_raw, str):
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
        else:
            tags = [str(t).strip() for t in tags_raw if str(t).strip()]

        blogs = load_blogs()
        new_blog = {
            'id': str(int(time.time() * 1000)),
            'title': title,
            'subtitle': subtitle,
            'author': author,
            'category': category,
            'tags': tags if tags else [category],
            'date': datetime.now().strftime('%B %d, %Y'),
            'read_time': calculate_read_time(content),
            'content': content
        }
        blogs.insert(0, new_blog)
        save_blogs(blogs)

        return jsonify({'status': 'success', 'blog': new_blog}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def clean_ai_response(text):
    """
    Sanitize and strip any AI model chain-of-thought, internal monologue,
    meta-reasoning bullet points, or scratchpad tags.
    """
    if not text:
        return ""
        
    # Strip <thought>...</thought> or <thinking>...</thinking> tags if present
    text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove meta-bullet headers output by thinking models
    lines = text.split('\n')
    clean_lines = []
    in_meta_block = True
    
    for line in lines:
        stripped = line.strip()
        # Detect meta-reasoning bullet points or scratchpad headers
        if in_meta_block and (
            stripped.startswith('- Role:') or 
            stripped.startswith('• Role:') or 
            stripped.startswith('* Role:') or 
            stripped.startswith('- Task:') or 
            stripped.startswith('- Constraint:') or 
            stripped.startswith('Constraint:') or 
            stripped.startswith('- Wait,') or 
            stripped.startswith('- If there is') or 
            stripped.startswith('- I should') or 
            stripped.startswith('Decision:') or 
            stripped.startswith('Thinking Process:') or 
            stripped.startswith('Thought:')
        ):
            continue
        
        # Once normal text starts, keep all lines
        if stripped and not (
            stripped.startswith('- Role:') or 
            stripped.startswith('• Role:') or 
            stripped.startswith('- Task:') or 
            stripped.startswith('- Constraint:') or 
            stripped.startswith('Constraint:') or 
            stripped.startswith('- Wait,') or 
            stripped.startswith('- If there is') or 
            stripped.startswith('- I should') or 
            stripped.startswith('Decision:')
        ):
            in_meta_block = False
            
        if not in_meta_block:
            clean_lines.append(line)
        
    result = '\n'.join(clean_lines).strip()
    return result if result else text.strip()


def generate_claude_hint(user_input, api_key):
    """
    Generate math hint using Anthropic Claude API (https://api.anthropic.com/v1/messages).
    Supports claude-3-5-sonnet, claude-3-5-haiku, and claude-3-haiku.
    """
    import urllib.request
    import urllib.error

    system_prompt = (
        "You are HintSpark, a helpful AI math tutor.\n"
        "STRICT OUTPUT RULES:\n"
        "- Respond ONLY with your final message to the user.\n"
        "- NEVER output your thought process, internal monologue, constraint analysis, or task bullet points.\n"
        "- If the user greets you (e.g., 'hi', 'hello'), respond with a friendly greeting and ask how you can help with math.\n"
        "- If given a math problem, provide a short, direct hint formatted with LaTeX ($...$ for inline, $$...$$ for display)."
    )

    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307"
    ]

    last_err = None

    for model in models_to_try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": f"Problem: {user_input}\n\nHint:"}
            ]
        }
        
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result and 'content' in result and len(result['content']) > 0:
                    return result['content'][0].get('text', '')
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"Claude HTTPError ({model}): {e.code} {err_body}")
            last_err = f"Claude API Error: {err_body}"
            if e.code == 401:
                raise Exception("Invalid Claude API Key (401 Unauthorized). Please check your Anthropic API Key.")
        except Exception as e:
            print(f"Claude request error ({model}): {e}")
            last_err = str(e)
            
    raise Exception(last_err or "Failed to generate response from Claude API.")


@app.route('/get_hint', methods=['POST'])
def get_hint():
    """
    POST /get_hint
    Generate a guided hint for a math problem using Gemini API or Anthropic Claude API.
    Automatically detects provider based on key format (sk-ant-... -> Claude, AIza... -> Gemini).
    """
    try:
        data = request.json or {}
        user_input = data.get('prompt', '').strip()
        
        if not user_input:
            return jsonify({
                'status': 'error',
                'message': 'Prompt cannot be empty.'
            }), 400

        # Resolve API Key: Prefer client-provided key from header/payload, fallback to server .env key
        client_key = (request.headers.get('X-Gemini-API-Key') or data.get('api_key', '')).strip().strip('"').strip("'")
        env_key = (os.getenv("GEMINI_API_KEY") or os.getenv("CLAUDE_API_KEY") or os.getenv("API") or '').strip().strip('"').strip("'")
        effective_api_key = client_key or env_key

        if not effective_api_key:
            return jsonify({
                'status': 'error',
                'message': 'API Key Required: Please enter your Google Gemini or Anthropic Claude API key in Settings (⚙️).'
            }), 400

        # ----------------------------------------------------------------------
        # MULTI-PROVIDER ROUTING: Detect Anthropic Claude vs Google Gemini Key
        # ----------------------------------------------------------------------
        if effective_api_key.startswith('sk-ant-') or effective_api_key.startswith('sk-'):
            # Route request to Anthropic Claude Provider
            try:
                response_text = generate_claude_hint(user_input, effective_api_key)
                return jsonify({
                    'status': 'success',
                    'response': clean_ai_response(response_text),
                    'provider': 'Anthropic Claude'
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 400

        # Re-configure genai with effective API key for Gemini request
        genai.configure(api_key=effective_api_key)

        # Formulate system instruction for tutor persona
        system_prompt = (
            "You are HintSpark, a helpful AI math tutor.\n"
            "STRICT OUTPUT DIRECTIVE:\n"
            "- Output ONLY your final direct response to the user.\n"
            "- NEVER include internal thinking, scratchpads, role/task bullet points, reasoning steps, constraints, or decisions in your output.\n"
            "- If user greets you, respond politely and ask how you can assist with math.\n"
            "- If given a math problem, provide a short, clear hint formatted with standard LaTeX ($...$ or $$...$$)."
        )

        # Gemini model candidate list to attempt dynamically
        candidate_models = [
            'gemini-1.5-flash',
            'gemini-2.0-flash',
            'gemini-2.5-flash',
            'gemini-1.5-flash-8b',
            'gemini-1.5-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-flash-latest'
        ]

        # Discover supported models from API list if possible
        try:
            discovered_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    name = m.name.replace('models/', '')
                    discovered_models.append(name)
                    discovered_models.append(m.name)
            if discovered_models:
                candidate_models = discovered_models + [m for m in candidate_models if m not in discovered_models]
        except Exception as e:
            print(f"Note: list_models fallback check: {e}")

        response_text = None
        last_error = None

        # Try generating hint with candidates until one succeeds
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt,
                )
                res = model.generate_content(
                    contents=f"Problem: {user_input}\n\nHint:",
                    generation_config={"candidate_count": 1},
                    stream=False
                )
                if res and hasattr(res, 'text') and res.text:
                    response_text = res.text
                    break
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                last_error = e
                continue

        if response_text:
            return jsonify({
                'status': 'success',
                'response': clean_ai_response(response_text)
            })
        else:
            err_msg = str(last_error) if last_error else 'No available Gemini model could process the request.'
            return jsonify({
                'status': 'error',
                'message': f'Failed to generate response: {err_msg}'
            }), 500

    except generation_types.BlockedPromptError as e:
        print(f"BlockedPromptError: {e}")
        return jsonify({
            'status': 'error',
            'message': 'The response was blocked due to safety concerns. Please try rephrasing your problem.'
        }), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Application entry point
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
