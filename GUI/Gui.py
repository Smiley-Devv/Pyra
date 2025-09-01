import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import subprocess
import sys
import os
import re
import urllib.request
import zipfile

# ---------------- CONFIG ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PYRA_HOME = os.path.join(os.path.expanduser("~"), "PyraRunner")
PACKAGE_DIR = os.path.join(PYRA_HOME, "packages")
os.makedirs(PACKAGE_DIR, exist_ok=True)

PACKAGE_METADATA = {
    "pyramath": {
        "description": "Provides math utilities for Pyra.",
        "example": 'import pyramath\nprint(pyramath.add(2,3))',
        "url": "https://github.com/Smiley-Devv/PyraPackages/raw/main/pyramath.zip"
    },
    "pyra-http": {
        "description": "Allows HTTP GET requests.",
        "example": 'import pyra_http\nresp = pyra_http.get("https://api.github.com")\nprint(resp["status_code"])',
        "url": "https://github.com/Smiley-Devv/PyraPackages/raw/main/pyra-http.zip"
    },
    "pyra-json": {
        "description": "Simple JSON parsing for Pyra.",
        "example": 'import pyra_json\nobj = pyra_json.parse("{\\"a\\":1}")\nprint(obj["a"])',
        "url": "https://github.com/Smiley-Devv/PyraPackages/raw/main/pyra-json.zip"
    }
}

# ---------------- GUI CLASS ----------------
class PyraGUI(ctk.CTk):
    KEYWORDS = ["if", "while", "for", "return", "print", "import"]
    BLOCK_KEYWORDS = ["if", "while", "for"]
    STRING_PATTERN = r'".*?"'
    NUMBER_PATTERN = r'\b\d+(\.\d+)?\b'

    def __init__(self):
        super().__init__()
        self.title("Pyra Runner")
        self.geometry("1000x700")
        self.filename = None

        # Tabs
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add("Editor")
        self.tabs.add("Package Manager")

        # --- Editor tab ---
        self.editor_frame = self.tabs.tab("Editor")
        self.line_numbers = ctk.CTkTextbox(self.editor_frame, width=5, state="disabled")
        self.line_numbers.pack(side="left", fill="y")
        self.text = ctk.CTkTextbox(self.editor_frame, wrap="none")
        self.text.pack(side="right", fill="both", expand=True)
        self.text.bind("<KeyRelease>", self.on_key_release)
        self.text.bind("<Return>", self.auto_indent)

        self.run_button = ctk.CTkButton(self.editor_frame, text="Run", command=self.run_code_thread)
        self.run_button.pack(fill="x")
        self.output = ctk.CTkTextbox(self.editor_frame, height=10, wrap="none", state="disabled")
        self.output.pack(fill="both", expand=False)

        # --- Package Manager tab ---
        self.pkg_frame = self.tabs.tab("Package Manager")
        self.pkg_listbox = ctk.CTkTextbox(self.pkg_frame, width=30)
        self.pkg_listbox.pack(side="left", fill="y")
        self.pkg_listbox.configure(state="disabled")
        self.pkg_listbox.bind("<ButtonRelease-1>", self.show_package_info)
        self.pkg_info = ctk.CTkTextbox(self.pkg_frame, state="disabled", wrap="word")
        self.pkg_info.pack(side="right", fill="both", expand=True)

        self.load_packages()
        self.update_line_numbers()

    # -------------- File operations ----------------
    def open_file(self):
        file = filedialog.askopenfilename(filetypes=[("Pyra Files", "*.pyra"), ("All Files", "*.*")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                self.text.delete("1.0", "end")
                self.text.insert("1.0", f.read())
            self.filename = file
            self.highlight_syntax()

    def save_file(self):
        if self.filename:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", "end"))
            self.highlight_syntax()
        else:
            self.save_as()

    def save_as(self):
        file = filedialog.asksaveasfilename(defaultextension=".pyra",
                                            filetypes=[("Pyra Files", "*.pyra"), ("All Files", "*.*")])
        if file:
            self.filename = file
            self.save_file()

    # -------------- Syntax highlighting ----------------
    def highlight_syntax(self, event=None):
        content = self.text.get("1.0", "end")
        self.text.tag_remove("keyword", "1.0", "end")
        self.text.tag_remove("string", "1.0", "end")
        self.text.tag_remove("number", "1.0", "end")

        for kw in self.KEYWORDS:
            for match in re.finditer(rf"\b{kw}\b", content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text.tag_add("keyword", start, end)

        for match in re.finditer(self.STRING_PATTERN, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add("string", start, end)

        for match in re.finditer(self.NUMBER_PATTERN, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text.tag_add("number", start, end)

    # -------------- Line numbers ----------------
    def update_line_numbers(self):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        row, _ = self.text.index("end").split(".")
        for i in range(1, int(row)):
            self.line_numbers.insert("end", f"{i}\n")
        self.line_numbers.configure(state="disabled")
        self.after(100, self.update_line_numbers)

    # -------------- Auto-indent ----------------
    def auto_indent(self, event=None):
        line = self.text.get("insert linestart", "insert")
        indent = re.match(r"\s*", line).group(0)
        last_word = line.strip().split(" ")[0] if line.strip() else ""
        if last_word in self.BLOCK_KEYWORDS:
            indent += "    "
        self.text.insert("insert", "\n" + indent)
        return "break"

    def on_key_release(self, event=None):
        self.highlight_syntax()
        self.update_line_numbers()

    # -------------- Run code ----------------
    def run_code_thread(self):
        if not self.filename:
            messagebox.showwarning("No file", "Save your code before running!")
            return
        self.save_file()
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", f"Running {self.filename}...\n")
        self.output.configure(state="disabled")

        def target():
            pyra_path = os.path.join(PYRA_HOME, "Pyra.py")
            if not os.path.exists(pyra_path):
                self.output.configure(state="normal")
                self.output.insert("end", f"Error: Pyra interpreter not found at {pyra_path}\n")
                self.output.configure(state="disabled")
                return
            result = subprocess.run([sys.executable, pyra_path, self.filename],
                                    capture_output=True, text=True, check=False)
            self.output.configure(state="normal")
            self.output.insert("end", result.stdout)
            if result.stderr:
                self.output.insert("end", "\nErrors:\n" + result.stderr)
            self.output.configure(state="disabled")

        threading.Thread(target=target).start()

    # -------------- Package Manager ----------------
    def load_packages(self):
        self.pkg_listbox.configure(state="normal")
        self.pkg_listbox.delete("1.0", "end")
        for pkg in os.listdir(PACKAGE_DIR):
            self.pkg_listbox.insert("end", pkg + "\n")
        self.pkg_listbox.configure(state="disabled")

    def show_package_info(self, event=None):
        index = self.pkg_listbox.index("insert").split(".")[0]
        pkg_name = self.pkg_listbox.get(f"{index}.0", f"{index}.end").strip()
        meta = PACKAGE_METADATA.get(pkg_name, {"description": "No description", "example": ""})
        self.pkg_info.configure(state="normal")
        self.pkg_info.delete("1.0", "end")
        self.pkg_info.insert("end", f"Name: {pkg_name}\n\nDescription:\n{meta['description']}\n\nExample:\n{meta['example']}\n\n")
        btn = ctk.CTkButton(self.pkg_info, text="Install", command=lambda: self.install_package(pkg_name))
        self.pkg_info.window_create("end", window=btn)
        self.pkg_info.configure(state="disabled")

    def install_package(self, pkg_name):
        meta = PACKAGE_METADATA.get(pkg_name)
        if not meta:
            messagebox.showerror("Error", f"No metadata for package {pkg_name}")
            return
        url = meta["url"]
        local_zip = os.path.join(PACKAGE_DIR, f"{pkg_name}.zip")
        try:
            urllib.request.urlretrieve(url, local_zip)
            with zipfile.ZipFile(local_zip, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(PACKAGE_DIR, pkg_name))
            os.remove(local_zip)
            messagebox.showinfo("Installed", f"Package {pkg_name} installed successfully.")
            self.load_packages()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install {pkg_name}:\n{e}")

# ---------------- Run the GUI ----------------
if __name__ == "__main__":
    app = PyraGUI()
    app.mainloop()
