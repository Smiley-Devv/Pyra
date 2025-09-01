import sys
import os
import requests
import zipfile
import importlib.util
import importlib.abc

# --------------------
# Setup
# --------------------
PYRA_DIR = os.path.join(os.getcwd(), "packages")
os.makedirs(PYRA_DIR, exist_ok=True)

# Known Pyra packages (can expand easily)
PYRA_PACKAGES = {
    "pyramath": {
        "url": "https://github.com/Smiley-Devv/PyraPackages/raw/main/pyramath.zip",
        "description": "Extra math utilities (prime checking, factorials, etc.)",
        "example": "import pyramath\nprint(pyramath.is_prime(7))"
    },
    "pyra-json": {
        "url": "https://github.com/Smiley-Devv/PyraPackages/raw/main/pyra-json.zip",
        "description": "JSON helpers for reading/writing configs",
        "example": "import pyra_json\nprint(pyra_json.load('config.json'))"
    },
    "pyra-http": {
        "url": "https://github.com/Smiley-Devv/PyraPackages/raw/main/pyra-http.zip",
        "description": "HTTP requests (GET/POST) with simple API",
        "example": "import pyra_http\nprint(pyra_http.get('https://httpbin.org/get').text)"
    }
}

# --------------------
# Package Installer
# --------------------
def install_package(name):
    if name not in PYRA_PACKAGES:
        print(f"❌ Unknown package: {name}")
        return

    url = PYRA_PACKAGES[name]["url"]
    print(f"⬇️  Downloading {name} from {url}...")

    try:
        r = requests.get(url)
        r.raise_for_status()
    except Exception as e:
        print("❌ Download failed:", e)
        return

    zip_path = os.path.join(PYRA_DIR, f"{name}.zip")
    with open(zip_path, "wb") as f:
        f.write(r.content)

    # Extract into folder (replace - with _ for valid names)
    extract_path = os.path.join(PYRA_DIR, name.replace("-", "_"))
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    os.remove(zip_path)
    print(f"✅ Installed {name}")


# --------------------
# Package Lister
# --------------------
def list_packages():
    print("📦 Installed Pyra Packages:")
    for folder in os.listdir(PYRA_DIR):
        safe_name = folder.replace("_", "-")
        desc = PYRA_PACKAGES.get(safe_name, {}).get("description", "No description")
        print(f" - {safe_name}: {desc}")


# --------------------
# Custom Import Hook
# --------------------
class PyraFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # Only care about pyra-* names
        if fullname.startswith("pyra-"):
            safe_name = fullname.replace("-", "_")
            package_path = os.path.join(PYRA_DIR, safe_name)

            if not os.path.exists(package_path):
                raise ImportError(f"❌ Pyra package {fullname} not installed")

            init_file = os.path.join(package_path, "__init__.py")
            if not os.path.exists(init_file):
                # Fallback to first .py file inside
                py_files = [f for f in os.listdir(package_path) if f.endswith(".py")]
                if py_files:
                    init_file = os.path.join(package_path, py_files[0])
                else:
                    raise ImportError(f"❌ No entry file for {fullname}")

            return importlib.util.spec_from_file_location(fullname, init_file)
        return None

sys.meta_path.insert(0, PyraFinder())


# --------------------
# Script Runner
# --------------------
def run_script(fname):
    with open(fname, "r", encoding="utf-8") as f:
        code = f.read()
    print(f"▶️ Running {fname}...\n")
    exec(code, globals())


# --------------------
# CLI Entry
# --------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pyra <command> [args]")
        print("Commands:")
        print("   install <package>   Install a Pyra package")
        print("   list                List installed packages")
        print("   <file>.pyra         Run a Pyra script")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "install" and len(sys.argv) >= 3:
        install_package(sys.argv[2])
    elif cmd == "list":
        list_packages()
    elif cmd.endswith(".pyra"):
        run_script(cmd)
    else:
        print(f"❌ Unknown command: {cmd}")
