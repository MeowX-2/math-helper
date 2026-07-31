import google.genai as genai
genai.configure(api_key="abracadabra")
model = genai.GenerativeModel('gemini-1.5-flash')
try:
    response = model.generate_content("Hello")
    print("Success:", response.text)
except Exception as e:
    print("Error:", e)
