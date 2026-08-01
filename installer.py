"""
HintSpark Setup Wizard & Uninstaller
====================================
Interactive Windows Installer GUI for HintSpark Math Helper.
Handles installation, Start Menu / Desktop shortcut creation, 
Windows Registry uninstaller registration, and clean uninstallation.
"""

import os
import sys
import shutil
import zipfile
import subprocess
import winreg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "HintSpark"
APP_TITLE = "HintSpark — AI Math Tutor & Helper"
PUBLISHER = "MeowX Math Helper Team"
VERSION = "1.0.0"

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_default_install_dir():
    local_appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    return os.path.join(local_appdata, 'Programs', APP_NAME)

def get_start_menu_dir():
    appdata = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
    return os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs')

def get_desktop_dir():
    userprofile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
    return os.path.join(userprofile, 'Desktop')

def create_windows_shortcut(target_exe, shortcut_path, description=APP_TITLE):
    try:
        working_dir = os.path.dirname(target_exe)
        ps_script = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_exe}"
        $Shortcut.WorkingDirectory = "{working_dir}"
        $Shortcut.Description = "{description}"
        $Shortcut.Save()
        """
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
    except Exception as e:
        print(f"Error creating shortcut {shortcut_path}: {e}")

def register_uninstaller(install_dir, main_exe):
    try:
        uninstaller_exe = os.path.join(install_dir, "Uninstall_HintSpark.exe")
        key_path = fr"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_exe}" --uninstall')
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, VERSION)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, main_exe)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except Exception as e:
        print(f"Error registering uninstaller: {e}")

def unregister_uninstaller():
    try:
        key_path = fr"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
    except Exception:
        pass

def perform_uninstallation():
    install_dir = get_default_install_dir()
    
    # 1. Remove Start Menu shortcut
    start_menu_shortcut = os.path.join(get_start_menu_dir(), f"{APP_NAME}.lnk")
    if os.path.exists(start_menu_shortcut):
        try: os.remove(start_menu_shortcut)
        except Exception: pass

    # 2. Remove Desktop shortcut
    desktop_shortcut = os.path.join(get_desktop_dir(), f"{APP_NAME}.lnk")
    if os.path.exists(desktop_shortcut):
        try: os.remove(desktop_shortcut)
        except Exception: pass

    # 3. Unregister from Windows Registry
    unregister_uninstaller()

    # 4. Remove installation folder via script (since executable is running inside install_dir)
    cmd = f'timeout /t 2 /nobreak > NUL & rmdir /s /q "{install_dir}"'
    subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} Setup Wizard")
        self.root.geometry("540x360")
        self.root.resizable(False, False)
        
        # Windows dark/light palette matching style
        self.install_dir_var = tk.StringVar(value=get_default_install_dir())
        self.create_desktop_shortcut_var = tk.BooleanVar(value=True)
        self.create_start_menu_var = tk.BooleanVar(value=True)
        self.launch_after_var = tk.BooleanVar(value=True)
        
        self.setup_ui()

    def setup_ui(self):
        # Header banner
        header = tk.Frame(self.root, bg="#1e293b", height=70)
        header.pack(fill="x")
        
        lbl_title = tk.Label(header, text=APP_TITLE, font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e293b")
        lbl_title.pack(anchor="w", padx=20, pady=(12, 0))
        
        lbl_sub = tk.Label(header, text="Installer Setup Wizard", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b")
        lbl_sub.pack(anchor="w", padx=20)

        # Body container
        self.body = tk.Frame(self.root, padx=25, pady=20)
        self.body.pack(fill="both", expand=True)

        lbl_dest = tk.Label(self.body, text="Installation Folder:", font=("Segoe UI", 10, "bold"))
        lbl_dest.pack(anchor="w", pady=(0, 5))

        path_frame = tk.Frame(self.body)
        path_frame.pack(fill="x", pady=(0, 15))

        ent_path = ttk.Entry(path_frame, textvariable=self.install_dir_var, font=("Segoe UI", 9))
        ent_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = ttk.Button(path_frame, text="Browse...", command=self.browse_folder)
        btn_browse.pack(side="right")

        # Checkboxes
        chk_desktop = ttk.Checkbutton(self.body, text="Create a Desktop Shortcut", variable=self.create_desktop_shortcut_var)
        chk_desktop.pack(anchor="w", pady=4)

        chk_start = ttk.Checkbutton(self.body, text="Create a Start Menu Shortcut (Searchable in Windows)", variable=self.create_start_menu_var)
        chk_start.pack(anchor="w", pady=4)

        chk_launch = ttk.Checkbutton(self.body, text="Launch HintSpark after installation completes", variable=self.launch_after_var)
        chk_launch.pack(anchor="w", pady=4)

        # Progress bar
        self.progress = ttk.Progressbar(self.body, mode="determinate")
        self.progress.pack(fill="x", pady=(20, 5))
        
        self.lbl_status = tk.Label(self.body, text="Ready to install.", font=("Segoe UI", 9), fg="#64748b")
        self.lbl_status.pack(anchor="w")

        # Footer controls
        footer = tk.Frame(self.root, bg="#f1f5f9", height=50)
        footer.pack(fill="x", side="bottom")

        self.btn_cancel = ttk.Button(footer, text="Cancel", command=self.root.quit)
        self.btn_cancel.pack(side="right", padx=(5, 20), pady=10)

        self.btn_install = ttk.Button(footer, text="Install", command=self.start_install)
        self.btn_install.pack(side="right", padx=5, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.install_dir_var.get())
        if folder:
            self.install_dir_var.set(os.path.join(folder, APP_NAME))

    def start_install(self):
        self.btn_install.config(state="disabled")
        self.btn_cancel.config(state="disabled")
        self.lbl_status.config(text="Extracting program files...")
        self.progress["value"] = 20
        self.root.update()
        
        try:
            target_dir = self.install_dir_var.get()
            os.makedirs(target_dir, exist_ok=True)
            
            base_dir = get_base_dir()
            payload_zip = os.path.join(base_dir, "payload.zip")
            payload_dir = os.path.join(base_dir, "payload")
            
            # Extract files
            if os.path.exists(payload_zip):
                with zipfile.ZipFile(payload_zip, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
            elif os.path.exists(payload_dir):
                shutil.copytree(payload_dir, target_dir, dirs_exist_ok=True)
            else:
                # If running directly from source directory for testing
                dist_src = os.path.join(base_dir, "dist", APP_NAME)
                if os.path.exists(dist_src):
                    shutil.copytree(dist_src, target_dir, dirs_exist_ok=True)
                else:
                    raise Exception("Installer payload missing. Please run build_exe.py to package setup.")

            self.progress["value"] = 60
            self.lbl_status.config(text="Creating shortcuts & registering app...")
            self.root.update()

            main_exe = os.path.join(target_dir, f"{APP_NAME}.exe")
            
            # Copy self as uninstaller
            self_exe = sys.executable if getattr(sys, 'frozen', False) else None
            if self_exe and os.path.exists(self_exe):
                uninstaller_exe = os.path.join(target_dir, "Uninstall_HintSpark.exe")
                try: shutil.copy2(self_exe, uninstaller_exe)
                except Exception: pass

            # Create Start Menu Shortcut
            if self.create_start_menu_var.get():
                start_dir = get_start_menu_dir()
                os.makedirs(start_dir, exist_ok=True)
                create_windows_shortcut(main_exe, os.path.join(start_dir, f"{APP_NAME}.lnk"))

            # Create Desktop Shortcut
            if self.create_desktop_shortcut_var.get():
                desktop_dir = get_desktop_dir()
                os.makedirs(desktop_dir, exist_ok=True)
                create_windows_shortcut(main_exe, os.path.join(desktop_dir, f"{APP_NAME}.lnk"))

            # Register in Windows Add/Remove Programs
            register_uninstaller(target_dir, main_exe)

            self.progress["value"] = 100
            self.lbl_status.config(text="Installation successful!")
            self.root.update()

            messagebox.showinfo("Success", f"{APP_NAME} has been successfully installed on your computer!")
            
            if self.launch_after_var.get() and os.path.exists(main_exe):
                subprocess.Popen([main_exe], cwd=target_dir)

            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Installation Error", f"Failed to install {APP_NAME}:\n{str(e)}")
            self.btn_install.config(state="normal")
            self.btn_cancel.config(state="normal")
            self.lbl_status.config(text="Installation failed.")

def run_uninstall_gui():
    root = tk.Tk()
    root.withdraw()
    ans = messagebox.askyesno("Uninstall HintSpark", f"Are you sure you want to completely remove {APP_NAME} from your computer?")
    if ans:
        perform_uninstallation()
        messagebox.showinfo("Uninstalled", f"{APP_NAME} has been successfully removed.")
    sys.exit(0)

def main():
    if "--uninstall" in sys.argv:
        run_uninstall_gui()
    else:
        root = tk.Tk()
        app = InstallerGUI(root)
        root.mainloop()

if __name__ == '__main__':
    main()
