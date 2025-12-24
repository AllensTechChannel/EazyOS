import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import winsound
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- BSOD ----------------
def bsod():
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "bsod.py")])

# ---------------- Restart ----------------
def restart_program():
    parent.destroy()
    subprocess.run([sys.executable, "OS.py"])

# ---------------- Load credentials ----------------
def load_credentials(filename="credentials.txt"):
    try:
        with open(filename, "r") as f:
            line = f.readline().strip()
            if "," in line:
                return line.split(",", 1)
            else:
                messagebox.showerror("Error", "Invalid credentials file format.")
                return None, None
    except FileNotFoundError:
        messagebox.showerror("Error", "Credentials file not found.")
        return None, None

stored_username, stored_password = load_credentials()

# ---------------- Login logic ----------------
def validate_and_restart():
    userid = username_entry.get()
    password = password_entry.get()

    if userid == stored_username and password == stored_password:
        winsound.PlaySound('media/DING.wav', winsound.SND_FILENAME)
        messagebox.showinfo("Welcome", f"Welcome, {stored_username}")
        restart_program()
    else:
        winsound.PlaySound('media/CHORD.wav', winsound.SND_FILENAME)
        messagebox.showerror("Logon Failed", "Invalid user name or password")

# ---------------- GUI ----------------
parent = tk.Tk()
parent.title("EazyOS Logon")
parent.resizable(False, False)
parent.configure(bg="#C0C0C0")

# Center window (Win98 style)
WIDTH, HEIGHT = 360, 220
screen_w = parent.winfo_screenwidth()
screen_h = parent.winfo_screenheight()
x = (screen_w - WIDTH) // 2
y = (screen_h - HEIGHT) // 2
parent.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

# -------- Main Beveled Frame --------
outer = tk.Frame(parent, bg="#808080", bd=2, relief="raised")
outer.pack(fill="both", expand=True, padx=6, pady=6)

inner = tk.Frame(outer, bg="#C0C0C0", bd=2, relief="sunken")
inner.pack(fill="both", expand=True)

font98 = ("MS Sans Serif", 9)

# -------- Title --------
tk.Label(
    inner,
    text="Enter Network Password",
    bg="#000080",
    fg="white",
    font=("MS Sans Serif", 9, "bold"),
    anchor="w",
    padx=6
).pack(fill="x")

content = tk.Frame(inner, bg="#C0C0C0")
content.pack(padx=12, pady=14)

# -------- Username --------
tk.Label(content, text="User name:", bg="#C0C0C0", font=font98).grid(row=0, column=0, sticky="e", pady=4)
username_entry = tk.Entry(content, font=font98, relief="sunken", bd=2)
username_entry.grid(row=0, column=1, pady=4)

# -------- Password --------
tk.Label(content, text="Password:", bg="#C0C0C0", font=font98).grid(row=1, column=0, sticky="e", pady=4)
password_entry = tk.Entry(content, show="*", font=font98, relief="sunken", bd=2)
password_entry.grid(row=1, column=1, pady=4)

# -------- Buttons --------
btn_frame = tk.Frame(inner, bg="#C0C0C0")
btn_frame.pack(pady=6)

login_btn = tk.Button(
    btn_frame,
    text="OK",
    width=8,
    font=font98,
    relief="raised",
    command=validate_and_restart
)
login_btn.grid(row=0, column=0, padx=6)

cancel_btn = tk.Button(
    btn_frame,
    text="Cancel",
    width=8,
    font=font98,
    relief="raised",
    command=parent.destroy
)
cancel_btn.grid(row=0, column=1, padx=6)

# -------- BSOD Shortcut --------
def trigger_bsod_and_exit():
    bsod()
    parent.after(150, parent.destroy)

parent.bind("<Control-Shift-B>", lambda e: trigger_bsod_and_exit())
parent.bind("<Escape>", lambda e: parent.destroy())

parent.mainloop()
