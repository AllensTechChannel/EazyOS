import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import winsound

# --- Restart function ---
def restart_program():
    parent.destroy()  # Close current window
    python_executable = sys.executable  # Current Python interpreter
    script_to_run = "OS.py"  # Script to run after restart
    subprocess.run([python_executable, script_to_run])

# --- Load credentials ---
def load_credentials(filename="credentials.txt"):
    try:
        with open(filename, "r") as f:
            line = f.readline().strip()
            if "," in line:
                username, password = line.split(",", 1)
                return username, password
            else:
                messagebox.showerror("Error", "Invalid credentials file format.")
                return None, None
    except FileNotFoundError:
        messagebox.showerror("Error", f"Credentials file '{filename}' not found.")
        return None, None

stored_username, stored_password = load_credentials()

# --- Validate login ---
def validate_and_restart():
    userid = username_entry.get()
    password = password_entry.get()

    if stored_username is None or stored_password is None:
        return  # Credentials not loaded

    if userid == stored_username and password == stored_password:
        winsound.PlaySound('media/DING.wav', winsound.SND_FILENAME)
        winsound.PlaySound(None, winsound.SND_PURGE)
        messagebox.showinfo("Login Successful", f"Welcome, {stored_username}!")  # Show username from file
        restart_program()  # Call restart after successful login
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# --- GUI setup ---
parent = tk.Tk()
parent.title("Login Form")
parent.attributes("-fullscreen", True)
parent.configure(bg="#008080")
parent.bind("<Escape>", lambda e: parent.destroy())

# Optional: Show username from file in GUI if loaded
if stored_username:
    tk.Label(parent, text=f"Username from file: {stored_username}", bg="#008080", fg="white", font=("Arial", 14)).pack(pady=10)

tk.Label(parent, text="Userid:").pack(pady=5)
username_entry = tk.Entry(parent)
username_entry.pack(pady=5)

tk.Label(parent, text="Password:").pack(pady=5)
password_entry = tk.Entry(parent, show="*")
password_entry.pack(pady=5)

# Login button
login_button = tk.Button(parent, text="Login", command=validate_and_restart)
login_button.pack(pady=10)

parent.mainloop()
