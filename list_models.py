import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("YOUR_GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    for m in models:
        print(m.name)
except Exception as e:
    print("Error:", e)
