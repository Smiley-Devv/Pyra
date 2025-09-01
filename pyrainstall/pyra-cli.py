import os
import sys
import json
import urllib.request
import zipfile

# Where Pyra packages live
PACKAGE_DIR = r"C:\Program Files\PyraRunner\Pyra Runner\packages"
os.makedirs(PACKAGE_DIR, exist_ok=True)

# A simple package index (could be a JSON hosted online)
PACKAGE_INDEX = {
    "pyramath": "https://github.com/Smiley-Devv/PyraPackages/raw/b45cb9b411d9608cabd699bfc42077cbdc72d527/pyramath.zip"
}

def install(package_name):
    if package_name not in PACKAGE_INDEX:
        print(f"Package '{package_name}' not found in index.")
        return
    
    url = PACKAGE_INDEX[package_name]
    print(f"Installing {package_name} from {url} ...")

    try:
        file_name, _ = urllib.request.urlretrieve(url)
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(PACKAGE_DIR)
        print(f"{package_name} installed successfully in {PACKAGE_DIR}")
    except PermissionError:
        print("Permission denied! Run this script as Administrator.")
    except Exception as e:
        print("Error installing package:", e)

def list_packages():
    print("Available packages in index:")
    for pkg in PACKAGE_INDEX:
        print("-", pkg)

def main():
    if len(sys.argv) < 2:
        print("Usage: pyra <command> [package_name]")
        print("Commands: install, list")
        return

    cmd = sys.argv[1].lower()
    if cmd == "install":
        if len(sys.argv) < 3:
            print("Please provide a package name to install.")
            return
        install(sys.argv[2])
    elif cmd == "list":
        list_packages()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
