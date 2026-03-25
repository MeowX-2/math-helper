import os
from flask import Flask, render_template, request, jsonify
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure your Gemini API Key
client = genai.Client(api_key=os.getenv("YOUR_GEMINI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/models', methods=['GET'])
def list_models():
    try:
        # Exclude non-text models (TTS, robotics, image-only, computer-use)
        EXCLUDE_KEYWORDS = ['tts', 'robotics', 'computer-use', '-image']

        models = client.models.list()
        model_names = []
        for m in models:
            # Only include Gemini text models that support generateContent
            actions = m.supported_actions or []
            is_gemini = m.name and m.name.startswith('models/gemini')
            supports_generate = 'generateContent' in actions
            is_excluded = any(kw in m.name for kw in EXCLUDE_KEYWORDS)
            if is_gemini and supports_generate and not is_excluded:
                model_names.append(m.name)
        model_names.sort(reverse=True)
        return jsonify({'status': 'success', 'models': model_names})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_hint', methods=['POST'])
def get_hint():
    try:
        data = request.json
        user_input = data.get('prompt', '')
        selected_model = data.get('model', 'gemini-2.5-flash')

        # Formulate the strict hint-only prompt with LaTeX preference
        system_prompt = (
            "You are a math tutor. Your task is to provide a helpful hint for the "
            "following math problem. Do not provide the solution. Focus on guiding "
            "the user to solve the problem themselves.\n\n"
            "IMPORTANT: When writing mathematical expressions, ALWAYS use LaTeX notation. "
            "Use $...$ for inline math and $$...$$ for display math. For example, "
            "write $x^2 - 4 = 0$ instead of x^2 - 4 = 0."
        )
        full_prompt = f"{system_prompt}\n\nProblem: {user_input}\n\nHint:"

        response = client.models.generate_content(
            model=selected_model,
            contents=full_prompt
        )

        return jsonify({
            'status': 'success',
            'response': response.text
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
