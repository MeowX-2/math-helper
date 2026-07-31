# HintSpark ✨ — Mathematical Insights & AI Math Assistant

HintSpark is a modern, responsive web application, desktop app, and Android-installable PWA for reading and publishing mathematical essays, complete with KaTeX expression rendering and an interactive **AI Math Assistant** powered by the **Google Gemini API**. 

Unlike standard AI search tools that immediately output solutions, HintSpark acts as a **guided math tutor**, providing hints and leading prompts to help users build problem-solving skills independently.

---

## Key Features

- 🤖 **Guided AI Math Tutor**: Get intelligent, hint-focused assistance for equations, calculus, geometry, and proofs.
- 📐 **LaTeX Math Rendering**: Inline (`$x^2 + y^2 = 1$`) and display (`$$\int_0^\infty f(x) dx$$`) math formatting rendered seamlessly via KaTeX.
- 📰 **Mathematical Essays & Feed**: Substack-style article grid with dynamic category navigation (*Number Theory*, *Calculus*, *Algebra*, *Geometry*) and live search.
- ✍️ **Article Publishing**: Publish community mathematical stories with automatic read-time estimation based on content and LaTeX complexity.
- 🌙 **Dark & Light Mode**: Instant theme switching with tailored contrast palettes.
- 📱 **Android & Desktop App Modes**: Install directly on Android/iOS via PWA, build an Android `.apk` via Bubblewrap, or run as a native desktop application (`desktop_app.py`).

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

## 📱 Mobile App & Android APK Creation Guide

### 1. Instant Android Installation (Zero Setup PWA)
HintSpark comes with pre-configured Progressive Web App (PWA) files (`manifest.json` + `sw.js`).

1. Deploy your app to **Render.com** (or any free hosting provider).
2. Open your live app URL in **Chrome on Android** (or Safari on iOS).
3. Tap the Chrome menu **(⋮)** in the top right.
4. Tap **"Install app"** or **"Add to Home screen"**.

🎉 **Result**: An official **HintSpark app icon** is placed on your Android home screen and app drawer, opening full-screen like a native mobile app!

---

### 2. Build Standalone Android APK (`.apk`)
To package HintSpark into an actual `.apk` file using Google's official **Bubblewrap CLI**:

1. Install Bubblewrap CLI:
   ```bash
   npm install -g @bubblewrap/cli
   ```
2. Initialize project from your live app manifest:
   ```bash
   bubblewrap init --manifest=https://your-deployed-app.onrender.com/static/manifest.json
   ```
3. Build the signed Android `.apk`:
   ```bash
   bubblewrap build
   ```
This generates `app-release-signed.apk`, which you can copy to any Android device and tap to install!

---

### 3. Build Standalone Desktop Executable (`.exe` / `.app`)
To compile HintSpark into a standalone desktop executable installer:

```bash
pip install pyinstaller pywebview
pyinstaller --noconfirm --onedir --windowed --name "HintSpark" desktop_app.py
```
The output executable will be placed in `dist/HintSpark/`.

---

## 🌐 Free Cloud Deployment Guide (Render.com)

To host your Flask AI backend on the web for 100% free with automatic GitHub deployments:

1. Push code to GitHub (`git push origin main`).
2. Go to [Render.com](https://render.com) and create a free Web Service connected to your repository.
3. Set **Build Command**: `pip install -r requirements.txt` and **Start Command**: `python app.py`.
4. In **Environment Variables**, add `GEMINI_API_KEY` = `your_gemini_api_key`.
5. Deploy! Your app will be live on `https://your-app.onrender.com`.

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