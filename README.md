# HintSpark ✨ — Mathematical Insights & AI Math Assistant

HintSpark is a modern, responsive web application and desktop/PWA app for reading and publishing mathematical essays, complete with KaTeX expression rendering and an interactive **AI Math Assistant** powered by the **Google Gemini API**. 

Unlike standard AI search tools that immediately output solutions, HintSpark acts as a **guided math tutor**, providing hints and leading prompts to help users build problem-solving skills independently.

---

## Key Features

- 🤖 **Guided AI Math Tutor**: Get intelligent, hint-focused assistance for equations, calculus, geometry, and proofs.
- 📐 **LaTeX Math Rendering**: Inline (`$x^2 + y^2 = 1$`) and display (`$$\int_0^\infty f(x) dx$$`) math formatting rendered seamlessly via KaTeX.
- 📰 **Mathematical Essays & Feed**: Substack-style article grid with dynamic category navigation (*Number Theory*, *Calculus*, *Algebra*, *Geometry*) and live search.
- ✍️ **Article Publishing**: Publish community mathematical stories with automatic read-time estimation based on content and LaTeX complexity.
- 🌙 **Dark & Light Mode**: Instant theme switching with tailored contrast palettes.
- 📱 **Desktop & PWA App Modes**: Run as a native OS desktop application (`desktop_app.py`) or install directly on mobile/desktop via Progressive Web App (PWA).

---

## Tech Stack

- **Backend**: Python 3.8+, Flask, `google-generativeai`, `python-dotenv`, `pywebview`
- **Frontend**: HTML5, CSS3 (Vanilla design tokens & CSS variables), Modern JavaScript (ES6+), `marked.js`
- **Math Rendering**: KaTeX (CDN auto-render)
- **AI Model**: Google Gemini API (`gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`)

---

## Setup & Installation Guide

Follow these steps to set up and run HintSpark locally on your machine.

### Prerequisites

- **Python 3.8+** installed.
- A **Google Gemini API Key** (obtainable for free from [Google AI Studio](https://aistudio.google.com/)).

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/math-helper.git
cd math-helper
```

---

### Step 2: Create & Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables (`.env`)

1. Copy `.env.example` to create your local `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your Google Gemini API key:
   ```env
   GEMINI_API_KEY="AIzaSyYourActualGeminiApiKeyHere"
   ```

> ⚠️ **Security Notice**: Never commit your `.env` file to version control. It is automatically ignored by `.gitignore`.

---

### Step 5: Run the Application

#### Option A: Web Mode (Flask Server)
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

#### Option B: Native Desktop App Mode
```bash
python desktop_app.py
```
Launches HintSpark inside a standalone desktop window (Windows, macOS, Linux).

---

## 📱 App Conversion Guide (Building Desktop Executables & PWA)

### 1. Build Standalone Desktop Executable (`.exe` / `.app`)
To compile HintSpark into a standalone executable installer that runs without opening a web browser:

```bash
pip install pyinstaller pywebview
pyinstaller --noconfirm --onedir --windowed --name "HintSpark" desktop_app.py
```
The compiled application output will be generated inside the `dist/HintSpark/` directory.

### 2. Progressive Web App (PWA) Installation
When hosted on any web server:
- **Desktop (Chrome/Edge)**: Click the **"Install App"** icon in the URL address bar.
- **Mobile (iOS / Android)**: Tap **"Add to Home Screen"** in Safari or Chrome to install HintSpark as a native mobile home screen app.

---

## Project Structure

```
math-helper/
├── .env.example              # Sample environment variable template
├── .gitignore                # Git ignore configuration (ignores .env, venvs, cache)
├── app.py                    # Flask application entry point & REST API routes
├── desktop_app.py            # Native OS Desktop application launcher (pywebview)
├── list_models.py            # Utility script to query available Gemini models
├── requirements.txt          # Python package dependencies (Flask, pywebview, etc.)
├── data/
│   └── blogs.json            # Local JSON storage for articles & stories
├── static/
│   ├── css/
│   │   └── style.css         # Main stylesheet (Design tokens, layouts, responsive design)
│   ├── js/
│   │   └── app.js            # Client-side logic (Fetch API, KaTeX renderer, Tutor drawer)
│   ├── manifest.json         # PWA Progressive Web App configuration manifest
│   └── sw.js                 # PWA Service Worker for offline shell caching
└── templates/
    ├── index.html            # Main parent layout template (includes PWA meta tags)
    └── components/           # Modular Jinja template partials
        ├── sidebar.html      # Sidebar navigation & theme toggle
        ├── header.html       # Workspace header & search input
        ├── hero.html         # Featured story hero card
        ├── ai_tutor.html     # AI Assistant drawer interface
        ├── publish_modal.html# Publish article form dialog
        └── reader_modal.html # Full article reader overlay
```

---

## API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves main application interface |
| `GET` | `/api/blogs` | Returns list of stories (supports `?category=` & `?search=`) |
| `POST` | `/api/blogs` | Publishes a new math essay |
| `POST` | `/get_hint` | Queries Gemini AI tutor model with a math prompt |

---

## Developer Utility Scripts

- **Check Available Gemini Models**:
  ```bash
  python list_models.py
  ```

---

## Contributing & License

Contributions, feedback, and pull requests are welcome! 

This project is open-source software licensed under the [MIT License](LICENSE).