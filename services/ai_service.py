"""
HintSpark — Multi-AI Provider Service Module
=============================================
Handles AI tutor prompt generation for Google Gemini API and Anthropic Claude API,
with automatic provider selection and response sanitization.
"""

import os
import re
import json
import urllib.request
import urllib.error
import google.generativeai as genai
from google.generativeai.types import generation_types


def clean_ai_response(text):
    """
    Sanitize and strip any AI model chain-of-thought, internal monologue,
    meta-reasoning bullet points, or scratchpad tags.
    """
    if not text:
        return ""
        
    text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE)

    lines = text.split('\n')
    clean_lines = []
    in_meta_block = True
    
    for line in lines:
        stripped = line.strip()
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
    """
    system_prompt = (
        "You are HintSpark, a helpful AI math tutor.\n"
        "STRICT OUTPUT DIRECTIVE:\n"
        "- Output ONLY your final direct response to the user.\n"
        "- NEVER include internal thinking, scratchpads, role/task bullet points, reasoning steps, constraints, or decisions in your output.\n"
        "- If user greets you, respond politely and ask how you can assist with math.\n"
        "- If given a math problem, provide a short, clear hint formatted with standard LaTeX ($...$ or $$...$$)."
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


def generate_gemini_hint(user_input, api_key):
    """
    Generate math hint using Google Gemini API.
    """
    genai.configure(api_key=api_key)

    system_prompt = (
        "You are HintSpark, a helpful AI math tutor.\n"
        "STRICT OUTPUT DIRECTIVE:\n"
        "- Output ONLY your final direct response to the user.\n"
        "- NEVER include internal thinking, scratchpads, role/task bullet points, reasoning steps, constraints, or decisions in your output.\n"
        "- If user greets you, respond politely and ask how you can assist with math.\n"
        "- If given a math problem, provide a short, clear hint formatted with standard LaTeX ($...$ or $$...$$)."
    )

    candidate_models = [
        'gemini-1.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash-8b',
        'models/gemini-1.5-flash',
        'models/gemini-2.0-flash'
    ]

    response_text = None
    last_error = None

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
        return response_text
    else:
        raw_err = str(last_error) if last_error else 'No available AI model could process the request.'
        if '429' in raw_err or 'Quota' in raw_err or 'quota' in raw_err:
            raise Exception("Gemini Free-Tier Rate Limit Reached (15 req/min). Please retry in ~25 seconds, or switch to a Claude API Key in Settings (⚙️).")
        raise Exception(f"AI Service Error: {raw_err}")


def get_tutor_hint(user_input, client_key_header=''):
    """
    Unified multi-provider AI hint generator.
    Routes to Anthropic Claude or Google Gemini based on key format.
    """
    user_input = (user_input or '').strip()
    if not user_input:
        raise ValueError('Prompt cannot be empty.')

    client_key = (client_key_header or '').strip().strip('"').strip("'")
    env_key = (os.getenv("GEMINI_API_KEY") or os.getenv("CLAUDE_API_KEY") or os.getenv("API") or '').strip().strip('"').strip("'")
    effective_api_key = client_key or env_key

    if not effective_api_key:
        raise Exception('API Key Required: Please enter your Google Gemini or Anthropic Claude API key in Settings (⚙️).')

    if effective_api_key.startswith('sk-ant-') or effective_api_key.startswith('sk-'):
        raw_response = generate_claude_hint(user_input, effective_api_key)
    else:
        raw_response = generate_gemini_hint(user_input, effective_api_key)

    return clean_ai_response(raw_response)
