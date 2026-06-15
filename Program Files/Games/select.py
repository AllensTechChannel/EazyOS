import tkinter as tk
import sys
import subprocess
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)
root = tk.Tk()
root.title("Launcher")
root.state("zoomed")

def open_mine():
    python_executable = sys.executable
    script_to_run = os.path.join("mine", "mine.py")
    subprocess.Popen([python_executable, script_to_run],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_guess():
    python_executable = sys.executable
    script_to_run = os.path.join("guess the number", "guess_the_number.py")
    subprocess.Popen([python_executable, script_to_run],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)

def open_pacman():
    python_executable = sys.executable
    script_to_run = os.path.join("pacman", "pacman.py")
    subprocess.Popen([python_executable, script_to_run],
                     creationflags=subprocess.CREATE_NEW_CONSOLE)

# Center area
frame = tk.Frame(root, bg="white")
frame.pack(fill="both", expand=True)

button_frame = tk.Frame(frame, bg="white")
button_frame.pack(expand=True)

pacman_btn = tk.Button(
    button_frame,
    text="Pacman",
    command=open_pacman,
    width=20,
    height=3
)

pacman_btn.pack(pady=10)

guess_btn = tk.Button(
    button_frame,
    text="Guess the Number",
    command=open_guess,
    width=20,
    height=3
)

guess_btn.pack(pady=10)

mine_btn = tk.Button(
    button_frame,
    text="Minesweeper",
    command=open_mine,
    width=20,
    height=3
)

mine_btn.pack(pady=10)


root.mainloop()
