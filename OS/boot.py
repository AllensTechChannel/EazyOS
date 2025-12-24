import tkinter as tk
from PIL import Image, ImageTk
import subprocess
from tkinter import Tk, messagebox
import sys
import time
root = tk.Tk()
root.title("EazyOS-Booting-hehehaha")
root.configure(bg="black")
import winsound
import winsound

winsound.PlaySound('media/bootsound.wav', winsound.SND_FILENAME)
def open_bios():
    import os
    os.startfile("bios.py")
    root.destroy
    sys.exit()
def on_key_press(event):
    # Check if Ctrl and Shift are held
    ctrl  = (event.state & 0x4) != 0
    alt = (event.state & 0x20000) != 0
    key = event.keysym.lower()
    
    if key == "f8":
        open_bios()  # Ctrl+Shift+F1 opens Notepad
        
    
# Bind key press events to root
root.bind("<Key>", on_key_press)
# === Fullscreen mode ===
root.attributes("-fullscreen", True)

# Exit fullscreen with ESC key
root.bind("<Escape>", lambda e: root.destroy())
root.configure(bg='black')

# Create a Label widget with black background and white text
label = tk.Label(root, text="Press F8 to Enter Setup", bg="black", fg="white", font=("Helvetica", 24))
label.pack(padx=20, pady=20)

# Create a Label widget with black background and white text
label = tk.Label(root, text="Loading EazyOS Logon...", bg="black", fg="white", font=("Helvetica", 24))
label.pack(padx=20, pady=20)
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
loading_label = tk.Label(center_frame, text=" 1", font=("Consolas", 20), fg="white", bg="black")
loading_label.pack(pady=20)

# === Animation logic ===
frames = ["|","|", "/","/", "-","-", "\\"]

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
    
# Play a WAV file

root.after(10000, finish)

root.mainloop()
