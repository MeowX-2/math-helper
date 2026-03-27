# Math Helper

A simple, AI-powered math tutor built with Flask, HTML/JS, and the Google Gemini API.

## Motive

The primary goal of **Math Helper** is to assist students in learning mathematics by providing **hints and structured guidance** rather than direct solutions. It acts as an interactive tutor that encourages critical thinking, helping users learn how to solve problems themselves step-by-step. The application seamlessly integrates LaTeX rendering to ensure that all mathematical expressions and equations are beautifully formatted and easy to read.

## Features & Benefits

- **Socratic Hint-Based Learning**: We don't just hand you the answer! Math Helper acts like a real tutor, providing structured, step-by-step guidance so *you* experience the incredibly rewarding "Aha!" moment of solving the problem yourself.
- **Powered by Google Gemini**: Built on the cutting-edge Gemini API, you get access to world-class language models. A built-in model selector lets you seamlessly switch between different Gemini models (like `gemini-2.5-flash`) to find the exact tutoring style that matches your needs!
- **Beautiful, Flawless LaTeX Rendering**: Math shouldn't be hard to read. Thanks to our slick KaTeX integration, complex formulas, fractions, and integrals render natively and beautifully on your screen. Say goodbye to deciphering unreadable plaintext math equations!
- **Lightning-Fast, Distraction-Free Interface**: Designed for maximum focus. Our clean, responsive, and modern chat interface is incredibly intuitive, making it a breeze to jump in, ask a question, and get unstuck instantly—whether you're on a laptop or your phone.
- **Your API, Your Rules**: Bring your own Gemini API key! This gives you total flexibility, security, and control over how you leverage the underlying AI models.

## Usage Manual

### Prerequisites

Ensure you have Python installed on your system. You will also need to obtain an API key from Google for using the Gemini API.

### Installation & Setup


1. **Install the required dependencies**:
   Install Flask, the Google GenAI SDK, and python-dotenv using pip:
   ```bash
   pip install flask google-genai python-dotenv
   ```

2. **Configure Environment Variables**:
   Create a new file named `.env` in the root directory of the project (if it doesn't exist) and add your Gemini API key:
   ```env
   YOUR_GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Run the application**:
   Start the Flask development server by running:
   ```bash
   python app.py
   ```

4. **Access the web app**:
   Open your preferred web browser and navigate to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

### How to Use the App

1. Once the application is open in your browser, you will be greeted by the Math Helper bot.
2. At the top of the interface, you can select which Gemini model you'd like to use (e.g., `gemini-2.5-flash`).
3. Type your math problem into the text box at the bottom (for example: *"How to solve $x^2 - 4 = 0$?"* or *"Help me integrate $x \sin(x)$"*).
4. Send the message. The bot will process your problem and return a formatted, helpful hint!
