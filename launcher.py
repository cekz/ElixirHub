# -----------------------------------------------------------------------------
# ELIXIR HUB - Open Source Project
# Copyright (C) 2025 [Libba/ElixirDev]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# -----------------------------------------------------------------------------

import os
import sys
import shutil
import time
import subprocess
import winshell
from win32com.client import Dispatch

# =============================================================================
#  CONNECTION BASE DATA
#  Configure your cloud infrastructure endpoints here before compiling.
# =============================================================================
CLOUD_URL = "YOUR_CONNECTION_URL_HERE"
CLOUD_KEY = "YOUR_PUBLIC_API_KEY_HERE"

# Bucket Configuration
# IMPORTANT: Replace these with the actual names of your storage buckets.
BUCKET_APP_CORE = "YOUR_APP_BUCKET_NAME"        # The bucket where the .exe is stored
BUCKETS_DATABASE = ["YOUR_DB_BUCKET_1", "YOUR_DB_BUCKET_2"] # Buckets for .json files

# File configuration
APP_EXECUTABLE_NAME = "Elixir.exe"
LAUNCHER_EXECUTABLE_NAME = "ElixirLauncher.exe"
SYSTEM_FOLDER_NAME = "ElixirHub"
# =============================================================================

# Dependency Check
try:
    from supabase import create_client, Client
except ImportError:
    print("CRITICAL ERROR: 'supabase' library is missing.")
    print("Please run: pip install supabase")
    input("Press Enter to exit...")
    sys.exit()

# System Paths (Installs in %LOCALAPPDATA% to avoid admin rights)
INSTALL_DIR = os.path.join(os.getenv('LOCALAPPDATA'), SYSTEM_FOLDER_NAME)
LINKS_DIR = os.path.join(INSTALL_DIR, "links")
APP_PATH = os.path.join(INSTALL_DIR, APP_EXECUTABLE_NAME)
LAUNCHER_PATH = os.path.join(INSTALL_DIR, LAUNCHER_EXECUTABLE_NAME)

def log(text, color="white"):
    """Prints colored log messages to console"""
    colors = {
        "green": "\033[92m", 
        "red": "\033[91m", 
        "blue": "\033[94m", 
        "reset": "\033[0m"
    }
    prefix = colors.get(color, "")
    print(f"{prefix}>> {text}{colors['reset']}")

def install_launcher_system():
    """Copies the launcher to the system folder for future self-updates"""
    current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    
    # If already running from install dir, do nothing
    if os.path.dirname(current_exe).lower() == INSTALL_DIR.lower():
        return

    log("Initializing system files...", "blue")
    try:
        shutil.copy2(current_exe, LAUNCHER_PATH)
    except Exception as e:
        log(f"Warning: Could not copy launcher: {e}", "red")

def create_desktop_shortcut():
    """Creates a shortcut pointing to the installed Launcher"""
    desktop = winshell.desktop()
    shortcut_path = os.path.join(desktop, "Elixir Hub.lnk")
    target = LAUNCHER_PATH 
    
    try:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = INSTALL_DIR
        shortcut.IconLocation = target
        shortcut.save()
    except Exception:
        pass 

def needs_update(local_path, cloud_info):
    """Compares local file size with cloud metadata"""
    if not os.path.exists(local_path):
        return True
    
    cloud_size = cloud_info.get('metadata', {}).get('size', 0)
    local_size = os.path.getsize(local_path)
    return local_size != cloud_size

def download_if_needed(client, bucket, filename, dest_path):
    """Downloads file only if size differs from cloud version"""
    try:
        # Get metadata first
        files_in_bucket = client.storage.from_(bucket).list()
        file_info = next((f for f in files_in_bucket if f['name'] == filename), None)
        
        if file_info and needs_update(dest_path, file_info):
            log(f"Downloading update: {filename}", "blue")
            data = client.storage.from_(bucket).download(filename)
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except Exception:
        pass # Ignore download errors to allow offline mode
    return False

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[95m")
    print("  ELIXIR | SYSTEM INSTALLER & UPDATER")
    print("  Open Source Edition")
    print("=======================================\033[0m")

    # 1. Configuration Safety Check
    # This prevents users from compiling the code without setting up their own buckets
    if "YOUR_" in CLOUD_URL or "YOUR_" in BUCKET_APP_CORE:
        log("CONFIGURATION ERROR:", "red")
        print("You must configure the 'CONNECTION BASE DATA' in launcher.py")
        print("Replace the 'YOUR_...' placeholders with your actual Cloud/Supabase details.")
        input("\nPress Enter to exit...")
        return

    # 2. Directory Setup
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)
    if not os.path.exists(LINKS_DIR):
        os.makedirs(LINKS_DIR)

    # 3. Self-Installation
    install_launcher_system()

    # 4. Connection & Updates
    try:
        # Connect to Cloud Data
        client: Client = create_client(CLOUD_URL, CLOUD_KEY)
        
        # Update Main App
        download_if_needed(client, BUCKET_APP_CORE, APP_EXECUTABLE_NAME, APP_PATH)
        
        # Update Databases (JSONs)
        print("Syncing databases...")
        for bucket in BUCKETS_DATABASE:
            try:
                files = client.storage.from_(bucket).list()
                for file in files:
                    name = file.get('name')
                    if name and name.endswith('.json'):
                        full_path = os.path.join(LINKS_DIR, name)
                        download_if_needed(client, bucket, name, full_path)
            except Exception:
                pass # Skip bucket if inaccessible (or if user didn't configure it)

    except Exception as e:
        log("Offline Mode: Cloud connection failed.", "red")

    # 5. Finalize
    create_desktop_shortcut()
    
    log("Launching application...", "green")
    time.sleep(1)
    
    # Launch the GUI App
    if os.path.exists(APP_PATH):
        subprocess.Popen([APP_PATH], cwd=INSTALL_DIR)
    else:
        log("Error: Application binary not found.", "red")
        log("Please check your internet connection and restart.", "red")
        input("Press Enter to close...")

if __name__ == "__main__":
    main()