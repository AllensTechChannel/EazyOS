import tkinter as tk
import time
import os
import sys
import subprocess
from tkinter import messagebox
import winsound
import ctypes

# --- Taskbar control (Windows only) ---
def hide_taskbar():
    taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        ctypes.windll.user32.ShowWindow(taskbar, 0)  # SW_HIDE

def show_taskbar():
    taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        ctypes.windll.user32.ShowWindow(taskbar, 5)  # SW_SHOW

# --- Startup Sound ---
winsound.PlaySound('media/The Microsoft Sound.wav', winsound.SND_FILENAME)
winsound.PlaySound(None, winsound.SND_PURGE)

# --- Core Functions ---
def on_button_click(event=None):
    try:
        x = my_button.winfo_rootx()
        y = my_button.winfo_rooty() + my_button.winfo_height()
        popup_menu.tk_popup(x, y)
    finally:
        popup_menu.grab_release()

def restart_program():
    winsound.PlaySound('media/DING.wav', winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)
    if messagebox.askokcancel("Restart", "Are you sure you want to restart?"):
        show_taskbar()
        root.destroy()
        subprocess.run([sys.executable, "boot.py"])

def exit_program():
    winsound.PlaySound('media/DING.wav', winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        winsound.PlaySound('media/win98logoff.wav', winsound.SND_FILENAME)
        winsound.PlaySound(None, winsound.SND_PURGE)
        show_taskbar()
        root.destroy()
        


def open_script():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "SYSTEM", "CMD.py")
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        print(f"Launching: {script_path}")
        subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open script:\n{e}")
import threading

def open_user():
    try:
        batch_file_path = os.path.join(os.path.dirname(__file__), "user.bat")
        if not os.path.exists(batch_file_path):
            raise FileNotFoundError(f"Batch file not found: {batch_file_path}")

        # Launch in a new command prompt window
        subprocess.Popen(["cmd.exe", "/c", batch_file_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

    except Exception as e:
        messagebox.showerror("Error", f"Could not open user script:\n{e}")



def run_program(script, hide=True):
    try:
        if hide:
            hide_taskbar()
        root.withdraw()
        subprocess.Popen([sys.executable, script], creationflags=subprocess.CREATE_NEW_CONSOLE).wait()
    except Exception as e:
        messagebox.showerror("Error", f"Could not open script:\n{e}")
    finally:
        if hide:
            show_taskbar()
        root.deiconify()

def open_game():
    run_program(r"..\Program Files\Games\select.py")

def open_txt():
    run_program(r"..\Program Files\notepad\notepad.py")

def open_sound():
    run_program(r"..\Program Files\Sound Player\music_player.py")

def open_internet():
    run_program(r"internet explorer\select.py")
def logout_program():
        winsound.PlaySound('media/CHIMES.wav', winsound.SND_FILENAME)
        winsound.PlaySound(None, winsound.SND_PURGE)
        show_taskbar()
        root.destroy()
        subprocess.run([sys.executable, "login.py"])

    
def open_about():
    run_program(r"about.py")

# --- Export Dummy Function ---


# --- Tkinter Main Window ---
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#008080")
root.bind("<Escape>", lambda e: (show_taskbar(), root.destroy()))

# --- Canvas and Taskbar ---
canvas = tk.Canvas(root, bg="#008080", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# --- Start Button ---
my_button = tk.Button(root, text="Start", command=on_button_click,
                      bg="#c3c3c3", fg="black", relief="flat",
                      activebackground="#a0a0a0", activeforeground="black")
button_window = canvas.create_window(0, 0, anchor="sw", window=my_button)

# --- Clock ---
clock_label = tk.Label(root, font=("Helvetica", 15), bg="#818181", fg="black")
clock_window = canvas.create_window(0, 0, anchor="se", window=clock_label)

# --- Clock Update ---
def update_time():
    clock_label.config(text=time.strftime('%H:%M:%S'))
    root.after(1000, update_time)
update_time()

# --- Popup Menu ---
popup_menu = tk.Menu(root, tearoff=0)
popup_menu.add_command(label="EazyOS", command=None)
popup_menu.add_separator()
popup_menu.add_command(label="About EazyOS", command=open_about)

popup_menu.add_separator()


# --- Export Submenu ---
programmenu = tk.Menu(root, tearoff=0)
programmenu.add_command(label="DOS Prompt", command=open_script)
programmenu.add_command(label="Games", command=open_game)
programmenu.add_command(label="Notepad", command=open_txt)
programmenu.add_command(label="Internet Explorer", command=open_internet)
programmenu.add_command(label="Media Player", command=open_sound)
programmenu.add_command(label="Change Username & Passowrd", command=open_user)
popup_menu.add_cascade(label="Programs", menu=programmenu)


# --- System Controls ---
popup_menu.add_separator()
popup_menu.add_command(label="Logout", command=logout_program)
popup_menu.add_command(label="Restart", command=restart_program)
popup_menu.add_command(label="Exit", command=exit_program)

# --- Right-click Context Menu ---
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Programs", command=None)
context_menu.add_separator()
context_menu.add_command(label="DOS Prompt", command=open_script)
context_menu.add_command(label="Games", command=open_game)
context_menu.add_command(label="Notepad", command=open_txt)
context_menu.add_command(label="Internet Explorer", command=open_internet)
context_menu.add_command(label="Media Player", command=open_sound)
root.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

# --- Draw Taskbar Layout ---
def draw_layout(event=None):
    canvas.delete("rect")
    width, height = canvas.winfo_width(), canvas.winfo_height()
    rect_height = 50
    canvas.create_rectangle(0, height - rect_height, width, height,
                            outline="black", width=2, fill="#818181", tags="rect")
    canvas.coords(button_window, 5, height - 5)
    canvas.coords(clock_window, width - 5, height - 5)

canvas.bind("<Configure>", draw_layout)

# --- Icons with Labels ---
icons = []
icon_start_x, icon_start_y, icon_spacing = 20, 20, 10

def add_icon_with_label(image_path, command, text, x, y):
    try:
        icon_img = tk.PhotoImage(file=image_path)
        icons.append(icon_img)
        btn = tk.Button(root, image=icon_img, command=command, bd=0)
        canvas.create_window(x, y, anchor="nw", window=btn)
        lbl_y = y + icon_img.height() + 2
        lbl = tk.Label(root, text=text, bg="#008080", fg="white", font=("Helvetica", 10))
        canvas.create_window(x + icon_img.width() // 2, lbl_y, anchor="n", window=lbl)
        return icon_img.height() + lbl.winfo_reqheight() + icon_spacing
    except Exception as e:
        print(f"{text} icon not found:", e)
        return 0

# Add desktop icons
icon_start_y += add_icon_with_label("SYSTEM/notepad.png", open_txt, "Notepad", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label("SYSTEM/group.png", open_game, "Games", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label("SYSTEM/player.png", open_sound, "Music", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label("SYSTEM/internet.png", open_internet, "Internet", icon_start_x, icon_start_y)

# --- Start Mainloop ---
root.mainloop()
