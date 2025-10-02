import tkinter as tk
from PIL import Image, ImageTk
import subprocess
from tkinter import Tk, messagebox
root = tk.Tk()
root.title("PythonOS-Booting")
root.configure(bg="black")

# === Fullscreen mode ===
root.attributes("-fullscreen", True)

# Exit fullscreen with ESC key
root.bind("<Escape>", lambda e: root.destroy())

# === Center frame ===
center_frame = tk.Frame(root, bg="black")
center_frame.pack(expand=True)

# === Load and display image ===
img = Image.open("python-logo.png")
tk_img = ImageTk.PhotoImage(img, master=root)
image_label = tk.Label(center_frame, image=tk_img, bg="black")
image_label.image = tk_img
image_label.pack()

# === Loading label below image ===
loading_label = tk.Label(center_frame, text=" |", font=("Consolas", 20), fg="white", bg="black")
loading_label.pack(pady=20)

# === Animation logic ===
frames = ["|", "/", "-", "\\"]
frame_index = 0
done = False

def animate():
    global frame_index
    if not done:
        loading_label.config(text=f" {frames[frame_index]}")
        frame_index = (frame_index + 1) % len(frames)
        root.after(100, animate)
    else:
        # Close this window before running OS.py
        root.destroy()
        # Run another script after animation finishes
        python_executable = "python"  # Or sys.executable for current interpreter
        script_to_run = "login.py"
        subprocess.run([python_executable, script_to_run])

# Start animation
animate()

# Stop after 5 seconds (demo)
def finish():
    global done
    done = True

root.after(5000, finish)

root.mainloop()
