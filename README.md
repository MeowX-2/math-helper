# HintSpark ✨ — Mathematical Insights & Multi-AI Math Assistant

HintSpark is a modern, responsive web application, native desktop app, and Android-installable PWA for reading and publishing mathematical essays, complete with KaTeX expression rendering and an interactive **Multi-AI Math Assistant** powered by **Google Gemini** and **Anthropic Claude**. 

Unlike standard AI search tools that immediately output solutions, HintSpark acts as a **guided math tutor**, providing hints and leading prompts to help users build problem-solving skills independently.

---

## Key Features

- 🤖 **Multi-AI Guided Tutor**: Multi-provider AI engine supporting **Google Gemini API** (`AIzaSy...`) and **Anthropic Claude API** (`sk-ant-...`) with automatic provider routing.
- 🔑 **Bring-Your-Own-Key (BYOK) & Quota Safety**: Visitors use their own API keys via the UI modal; server keys are kept secure and quota-protected.
- 📁 **Automated `.env` Generation**: Typing an API key into the UI automatically generates and configures a clean local `.env` file on disk.
- 📐 **LaTeX Math Rendering**: Inline (`$x^2 + y^2 = 1$`) and display (`$$\int_0^\infty f(x) dx$$`) math formatting rendered seamlessly via KaTeX.
- 📰 **Mathematical Essays & Feed**: Substack-style article grid with dynamic category navigation (*Number Theory*, *Calculus*, *Algebra*, *Geometry*) and live search.
- ✍️ **Article Publishing**: Publish community mathematical stories with automatic read-time estimation based on content and LaTeX complexity.
- 🌙 **Dark & Light Mode**: Instant theme switching with tailored contrast palettes.
- 📱 **Android & Desktop App Modes**: Install directly on Android/iOS via PWA, build an Android `.apk` via Bubblewrap, or run as a native desktop application (`desktop_app.py`).

---

## Tech Stack

- **Backend**: Python 3.8+, Flask, `google-generativeai`, `python-dotenv`, `pywebview`
- **Frontend**: HTML5, CSS3 (Vanilla design tokens & CSS variables), Modern JavaScript (ES6+), `marked.js`
- **AI Models Supported**: 
  - **Google Gemini**: `gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`
  - **Anthropic Claude**: `claude-3-5-sonnet`, `claude-3-5-haiku`, `claude-3-haiku`
- **Math Rendering**: KaTeX (CDN auto-render)

---

## Setup & Installation Guide

Follow these steps to set up and run HintSpark locally on your machine.

### Prerequisites

- **Python 3.8+** installed.
- A free **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/)) OR an **Anthropic Claude API Key** (from [Anthropic Console](https://console.anthropic.com/)).

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

2. Open `.env` and set your API key (either Gemini or Claude):
   ```env
   GEMINI_API_KEY="AIzaSyYourActualGeminiApiKeyHere"
   ```
   *Note: If you run the app and type your key in the UI **`⚙️ API Settings`** modal, it will generate this `.env` file automatically!*

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

## 🌐 Deploying Free to Cloud (Render.com)

**Yes! Render.com is the recommended free host.**

### How to Deploy on Render (100% Free):
1. Push your latest code to GitHub:
   ```bash
   git push origin main
   ```
2. Go to [Render.com](https://render.com) and create a free account.
3. Click **New +** -> **Web Service** and select your GitHub repository (`MeowX-2/math-helper`).
4. Configure service settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py` (or `gunicorn app:app`)
5. Click **Create Web Service**. 

🎉 **Done!** Render gives you a live public URL (e.g., `https://hintspark-math.onrender.com`). Anyone can open it on their phone or laptop, enter their API key in Settings, and use HintSpark anywhere!

---

## 🖥️ Desktop Application (.exe) & Easy Local Execution

### Option 1: Instant 1-Click Launch (Python Desktop Window)
Run HintSpark inside a native desktop application window:
```bash
python desktop_app.py
```
*This starts the backend and opens HintSpark directly inside a sleek native desktop window!*

---

### Option 2: Download or Build Windows Setup Installer (`HintSpark_Setup.exe`)
The recommended way to install HintSpark on Windows is using the **Setup Installer Wizard**:
1. Download **`HintSpark_Setup.exe`** from our [Releases Page](https://github.com/MeowX-2/math-helper/releases).
2. Double-click **`HintSpark_Setup.exe`** and click **Install**.
3. The setup wizard automatically:
   - Installs HintSpark to `%LOCALAPPDATA%\Programs\HintSpark`.
   - Creates a **Start Menu Shortcut** (so searching "HintSpark" in Windows search immediately opens it).
   - Creates a **Desktop Shortcut**.
   - Registers an entry in **Windows Settings / Control Panel (Add or Remove Programs)** for clean uninstallation.

### Option 3: Linux Desktop App (`HintSpark-Linux`)

#### Method A: Run via Launch Script
1. Clone the repo and navigate to the project directory:
   ```bash
   git clone https://github.com/MeowX-2/math-helper.git
   cd math-helper
   ```
2. Make `launch_linux.sh` executable and run it:
   ```bash
   chmod +x launch_linux.sh
   ./launch_linux.sh
   ```
   *(The script automatically creates a virtualenv, installs WebKit/PyWebView dependencies, and launches HintSpark).*

#### Method B: Build Standalone Linux Executable Tarball
1. Install system WebKit GTK dependencies (Debian/Ubuntu):
   ```bash
   sudo apt update
   sudo apt install -y python3-gi gir1.2-webkit2-4.0
   ```
2. Build with PyInstaller:
   ```bash
   pip install pyinstaller pywebview -r requirements.txt
   pyinstaller --noconfirm --onedir --windowed --name HintSpark --add-data "templates:templates" --add-data "static:static" --add-data "data:data" desktop_app.py
   ```
3. Run the compiled Linux app from `dist/HintSpark/HintSpark`.

---

If you prefer to build the setup installer from source:

1. Install PyInstaller & PyWebView (if not already installed):
   ```bash
   pip install pyinstaller pywebview
   ```
2. Run the automated build script:
   ```bash
   python build_exe.py
   ```
3. Your executable will be generated at:
   ```text
   dist/HintSpark/HintSpark.exe
   ```
   *You can double-click `HintSpark.exe` to run the application offline, or zip the `dist/HintSpark` folder to share with anyone!*

---

## Project Structure

```
math-helper/
├── .env.example              # Sample environment variable template
├── .gitignore                # Git ignore configuration (ignores .env, venvs, cache)
├── Procfile                  # Production WSGI server command (gunicorn app:app)
├── app.py                    # Application factory & WSGI server entry point
├── desktop_app.py            # Native OS Desktop application launcher (pywebview)
├── list_models.py            # Utility script to query available Gemini models
├── requirements.txt          # Python package dependencies
├── services/
│   ├── ai_service.py         # Multi-AI provider engine (Gemini & Claude + output sanitizer)
│   └── blog_service.py       # Article dataset storage, filtering & read-time calculations
├── routes/
│   ├── main_routes.py        # Web app shell & .env configuration API endpoints
│   └── api_routes.py         # REST API endpoints (/api/blogs & /get_hint)
├── data/
│   └── blogs.json            # Local JSON storage for articles & stories
├── static/
│   ├── css/
│   │   └── style.css         # Main design system stylesheet
│   ├── js/
│   │   └── app.js            # Client controller, KaTeX renderer & BYOK storage
│   ├── manifest.json         # PWA Progressive Web App configuration manifest
│   └── sw.js                 # PWA Service Worker for offline shell caching
└── templates/
    ├── index.html            # Main parent layout template
    └── components/           # Modular Jinja template partials
        ├── sidebar.html      # Sidebar navigation & theme toggle
        ├── header.html       # Workspace header & search input
        ├── hero.html         # Featured story hero card
        ├── ai_tutor.html     # AI Assistant drawer interface
        ├── settings_modal.html# Multi-Provider API Key setup modal
        ├── publish_modal.html# Publish article form dialog
        └── reader_modal.html # Full article reader overlay
```

---

## Contributing & License

Contributions, feedback, and pull requests are welcome! 

This project is open-source software licensed under the [MIT License](LICENSE).