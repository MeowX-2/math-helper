import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()
api_key = os.getenv("API")
genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content("Hello")
    print("Success:", response.text)
except Exception as e:
    print("Error:", e)
