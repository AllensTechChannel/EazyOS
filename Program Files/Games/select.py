import tkinter as tk
import sys
import subprocess
import os

root = tk.Tk()
root.title("Launcher")
root.state("zoomed")  # start maximized instead of fullscreen

def open_toe():
    # Launch another Python script
    python_executable = sys.executable
    script_to_run = os.path.join("..", "Program Files", "Games", "tic-tac-toe", "tic-tac-toe.py")
    subprocess.Popen([python_executable, script_to_run])

try:
    # Create a canvas that expands with the window
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill="both", expand=True)

    # Load icon and create button
    icon_path = os.path.join("..", "Program Files", "Games", "tic-tac-toe", "tic-tac-toe.png")
    icon_image = tk.PhotoImage(file=icon_path)
    icon_button = tk.Button(root, image=icon_image, command=open_toe, bd=0)

    # Place icon at the top-left corner
    canvas.create_window(20, 20, anchor="nw", window=icon_button)

except Exception as e:
    print("Icon image not found:", e)

root.mainloop()
