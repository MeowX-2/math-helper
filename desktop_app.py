"""
HintSpark — Native Desktop Application Launcher
================================================
Launches the HintSpark Flask application inside a native desktop OS window
using pywebview. Requires `pip install pywebview`.

To build a standalone .exe or .app executable:
    pip install pyinstaller pywebview
    pyinstaller --noconfirm --onedir --windowed --name "HintSpark" desktop_app.py
"""

import sys
import threading
import webview
from app import app


def start_flask():
    """Run Flask development server silently on localhost."""
    # Run on port 5000 in quiet mode
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    # Start Flask backend thread
    server_thread = threading.Thread(target=start_flask, daemon=True)
    server_thread.start()

    # Create native desktop application window
    webview.create_window(
        title='HintSpark — AI Math Assistant',
        url='http://127.0.0.1:5000',
        width=1280,
        height=840,
        min_size=(900, 600),
        resizable=True,
        confirm_close=False
    )

    # Start OS webview main loop
    webview.start()
