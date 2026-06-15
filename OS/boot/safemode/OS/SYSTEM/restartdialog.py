import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import winsound
import os
import logging
import time

# === CONSTANTS ===
WIN98_BLUE = "#000080"
WIN98_GRAY = "#C0C0C0"
WIN98_DARK_GRAY = "#808080"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EazyOS is Restarting...")
        self.root.resizable(False, False)
        self.root.configure(bg=WIN98_GRAY)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_ui()
        
    def _on_closing(self):
        self.root.destroy()

    def _create_ui(self):
        """Create the restart UI"""
        # Main beveled frame
        outer = tk.Frame(self.root, bg=WIN98_DARK_GRAY, bd=2, relief="raised")
        outer.pack(fill="both", expand=True, padx=6, pady=6)

        inner = tk.Frame(outer, bg=WIN98_GRAY, bd=2, relief="sunken")
        inner.pack(fill="both", expand=True)

        font98 = ("MS Sans Serif", 9)
        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)

        self.root.geometry(f"+{x}+{y}")
        # Title bar
        tk.Label(
            inner,
            text="EazyOS is Restarting...",
            bg=WIN98_BLUE,
            fg="white",
            font=("MS Sans Serif", 9, "bold"),
            anchor="w",
            padx=6
        ).pack(fill="x")

        # Content area
        content = tk.Frame(inner, bg=WIN98_GRAY)
        content.pack(padx=12, pady=14)

        # Status message
        tk.Label(
            content,
            text="Please Wait While EazyOS Restarts.",
            bg=WIN98_GRAY,
            fg="black",
            font=("MS Sans Serif", 9, "bold"),
        ).pack(pady=8)

    def _finish(self):
        boot_path = os.path.abspath(
            os.path.join(BASE_DIR, "..", "..", "..", "..", "boot.py")
    )

        print("boot_path =", boot_path)
        print("exists =", os.path.exists(boot_path))
 
        subprocess.Popen(
            [sys.executable, boot_path],
            cwd=os.path.dirname(boot_path)
    )

        self.root.destroy()

if __name__ == "__main__":
    try:
        app = LoginWindow()
        # FIX: added 4000ms delay so the window renders before closing
        app.root.after(4000, app._finish)
        app.root.mainloop()
    except Exception as e:
        logging.exception("Error during restart window")
