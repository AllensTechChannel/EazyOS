import tkinter as tk
from tkinter import ttk
import sys
import subprocess
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def add_blinking_cursor(root):
    cursor = tk.Label(root, text="_", fg="white", bg="#0000AA", font=("Consolas", 14))
    cursor.place(x=50, y=500)  # Adjust position as needed

    def blink():
        current = cursor.cget("text")
        cursor.config(text="" if current == "_" else "_")
        root.after(500, blink)  # Blink every 500ms

    blink()

def add_progress_bar(root):
    progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress.place(relx=0.5, rely=0.9, anchor="center")

    percent_label = tk.Label(root, text="0% complete", fg="white", bg="#0000AA", font=("Consolas", 12))
    percent_label.place(relx=0.5, rely=0.95, anchor="center")

    # Fake system messages
    messages = [
        "Checking disk for errors...",
        "Loading drivers...",
        "Verifying system integrity...",
        "Scanning memory...",
        "Applying security patches...",
        "Finalizing setup..."
    ]
    msg_label = tk.Label(root, text="", fg="white", bg="#0000AA", font=("Consolas", 12))
    msg_label.place(relx=0.5, rely=0.85, anchor="center")

    def step():
        if progress["value"] < 100:
            # Random increment between 1 and 10
            progress["value"] += random.randint(1, 10)
            if progress["value"] > 100:
                progress["value"] = 100

            # Update percentage text
            percent_label.config(text=f"{progress['value']}% complete")

            # Show a random system message
            msg_label.config(text=random.choice(messages))

            # Random delay between 200ms and 800ms
            delay = random.randint(200, 800)
            root.after(delay, step)
        else:
            # Once complete, launch boot.py
            subprocess.run([sys.executable, os.path.join(BASE_DIR, "boot.py")])
            exit   
    step()

def fake_bsod():
    root = tk.Tk()
    root.title("EazyOS-Blue Screen of Death")
    root.attributes("-fullscreen", True)
    root.configure(bg="#0000AA")

    # Disable closing
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.bind("<Alt-F4>", lambda e: "break")
    root.bind("<Escape>", lambda e: root.destroy())

    message = (
        "A problem has been detected and Windows has been shut down to prevent damage\n"
        "to your computer.\n\n"
        "PROGRAM FORCE CLOSE \n\n"
        "If this is the first time you've seen this Stop error screen,\n"
        "restart your computer. If this screen appears again, follow\n"
        "these steps:\n\n"
        "Check to make sure any new hardware or software is properly installed.\n"
        "If this is a new installation, ask your hardware or software manufacturer\n"
        "for any Windows updates you might need.\n\n"
        "Technical information:\n"
        "*** STOP: 0x0000007B (0xF78D2524, 0xC0000034, 0x00000000, 0x00000000)"
    )

    label = tk.Label(root, text=message, fg="white", bg="#0000AA",
                     font=("Consolas", 14), justify="left")
    label.pack(padx=50, pady=50, anchor="w")

    add_blinking_cursor(root)
    add_progress_bar(root)

    root.mainloop()

if __name__ == "__main__":
    fake_bsod()
