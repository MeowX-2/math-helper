"""
HintSpark — Windows Desktop Executable (.exe) Builder
=====================================================
Automated PyInstaller build script to generate standalone HintSpark.exe
"""

import os
import sys
import subprocess

def build():
    print("=" * 60)
    print(" HintSpark — Building Standalone Windows Executable (.exe)")
    print("=" * 60)

    # Specify data folder separators (Windows uses ';', Linux/macOS uses ':')
    sep = ';' if sys.platform.startswith('win') else ':'

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "HintSpark",
        "--add-data", f"templates{sep}templates",
        "--add-data", f"static{sep}static",
        "--add-data", f"data{sep}data",
        "desktop_app.py"
    ]

    print(f"\nRunning PyInstaller build command...\n")
    res = subprocess.run(cmd)

    if res.returncode == 0:
        print("\n" + "=" * 60)
        print(" SUCCESS! Desktop app executable generated at:")
        print(" dist/HintSpark/HintSpark.exe")
        print("=" * 60)
    else:
        print("\n Build encountered errors. Please verify dependencies.")

if __name__ == '__main__':
    build()
