import sys
import os
import urllib.request
import zipfile
import re
import types
import json
import requests

# -------------------------------
# Config
# -------------------------------
USER_HOME = os.path.expanduser("~")
PYRA_HOME = os.path.join(USER_HOME, "PyraRunner")
PACKAGE_DIR = os.path.join(PYRA_HOME, "packages")
os.makedirs(PACKAGE_DIR, exist_ok=True)

# -------------------------------
# Simple Interpreter
# -------------------------------
class Interpreter:
    def __init__(self):
        self.env = {"http": self.load_http(), "json": self.load_json()}

    def load_http(self):
        class Http:
            @staticmethod
            def get(url):
                r = requests.get(url)
                return types.SimpleNamespace(status_code=r.status_code, text=r.text)
        return Http()

    def load_json(self):
        class Json:
            @staticmethod
            def loads(s): return json.loads(s)
            @staticmethod
            def dumps(obj): return json.dumps(obj)
        return Json()

    def eval_line(self, line):
        try:
            # Use eval for expressions, exec for assignments/statements
            if "=" in line:
                exec(line, {}, self.env)
            else:
                result = eval(line, {}, self.env)
                if result is not None:
                    print(result)
        except Exception as e:
            print("Error:", e)

    def run_file(self, filepath):
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    self.eval_line(line)

# -------------------------------
# CLI
# -------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: pyra <file>")
        return
    file_path = sys.argv[1]
    interpreter = Interpreter()
    print(f"Running {file_path}...")
    interpreter.run_file(file_path)

if __name__ == "__main__":
    main()
