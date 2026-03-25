import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("YOUR_GEMINI_API_KEY")
print(f"Loaded API key: {api_key}")
client = genai.Client(api_key=api_key)
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Hello"
    )
    print("Success:", response.text)
except Exception as e:
    print("Error:", e)
