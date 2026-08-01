"""
HintSpark — Master Executable & Setup Installer Builder
======================================================
Builds:
1. dist/HintSpark/HintSpark.exe (Folder distribution)
2. dist/HintSpark_Setup.exe    (Full Windows GUI Installer Setup Wizard)
3. dist/HintSpark_Portable.exe (Single-file portable executable)
"""

import os
import sys
import shutil
import zipfile
import subprocess

def build():
    print("=" * 65)
    print(" HintSpark — Building Windows Executables & Setup Installer")
    print("=" * 65)

    sep = ';' if sys.platform.startswith('win') else ':'

    # Step 1: Build Primary App Directory Distribution
    print("\n[1/3] Building HintSpark directory executable (dist/HintSpark)...")
    cmd_dir = [
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
    res1 = subprocess.run(cmd_dir)
    if res1.returncode != 0:
        print("ERROR: Failed to build directory executable.")
        return

    # Step 2: Create payload zip for installer setup wizard
    print("\n[2/3] Packaging installer setup payload (payload.zip)...")
    dist_dir = os.path.join("dist", "HintSpark")
    payload_zip = "payload.zip"
    
    with zipfile.ZipFile(payload_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, dist_dir)
                zipf.write(abs_path, rel_path)
    
    print(f" Payload compressed: {os.path.getsize(payload_zip) / (1024*1024):.2f} MB")

    # Step 3: Build GUI Setup Installer (HintSpark_Setup.exe)
    print("\n[3/3] Compiling HintSpark_Setup.exe (Real Setup Installer Wizard)...")
    cmd_installer = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "HintSpark_Setup",
        "--add-data", f"payload.zip{sep}.",
        "installer.py"
    ]
    res2 = subprocess.run(cmd_installer)

    # Clean up temporary payload zip file
    if os.path.exists("payload.zip"):
        os.remove("payload.zip")

    if res2.returncode == 0:
        print("\n" + "=" * 65)
        print(" SUCCESS! Real App Installer & Executable Ready:")
        print(" -> GUI Setup Installer: dist/HintSpark_Setup.exe")
        print(" -> App Directory:        dist/HintSpark/HintSpark.exe")
        print("=" * 65)
    else:
        print("\n Build encountered errors building Setup Installer.")

if __name__ == '__main__':
    build()
