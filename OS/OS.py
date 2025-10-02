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
        show_taskbar()  # restore before quitting
        root.destroy()
        subprocess.run([sys.executable, "boot.py"])

def exit_program():
    winsound.PlaySound('media/DING.wav', winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        winsound.PlaySound('media/CHIMES.wav', winsound.SND_FILENAME)
        winsound.PlaySound(None, winsound.SND_PURGE)
        show_taskbar()  # restore before quitting
        root.destroy()

def open_script():
    try:
        root.withdraw()
        subprocess.Popen([sys.executable, r"SYSTEM\CMD.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open script:\n{e}")
    finally:
        root.deiconify()

def run_program(script, hide=True):
    try:
        if hide: hide_taskbar()
        root.withdraw()
        subprocess.Popen([sys.executable, script], creationflags=subprocess.CREATE_NEW_CONSOLE).wait()
    except Exception as e:
        messagebox.showerror("Error", f"Could not open script:\n{e}")
    finally:
        if hide: show_taskbar()
        root.deiconify()


def open_game():
    run_program(r"..\Program Files\Games\select.py")

def open_txt():
    run_program(r"..\Program Files\notepad\notepad.py")

def open_sound():
    run_program(r"..\Program Files\Sound Player\music_player.py")
def about():
    run_program(r"about.py")
def open_internet():
    run_program(r"internet explorer\select.py")
def open_about():
    run_program(r"about.py")



# --- Main window ---
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#008080")
root.bind("<Escape>", lambda e: (show_taskbar(), root.destroy()))

# --- Canvas ---
canvas = tk.Canvas(root, bg="#008080", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# --- Start button ---
my_button = tk.Button(root, text="Start", command=on_button_click,
                      bg="#c3c3c3", fg="black", relief="flat",
                      activebackground="#a0a0a0", activeforeground="black")
button_window = canvas.create_window(0, 0, anchor="sw", window=my_button)

# --- Clock label ---
clock_label = tk.Label(root, font=("Helvetica", 15), bg="#818181", fg="black")
clock_window = canvas.create_window(0, 0, anchor="se", window=clock_label)

# --- Popup menu ---
popup_menu = tk.Menu(root, tearoff=0)
popup_menu.add_command(label="EazyOS", command=None)
popup_menu.add_separator()
popup_menu.add_command(label="About EazyOS", command=open_about)
popup_menu.add_separator()
popup_menu.add_command(label="Programs", command=None)
popup_menu.add_separator()
popup_menu.add_command(label="DOS Prompt", command=open_script)
popup_menu.add_command(label="Games", command=open_game)
popup_menu.add_command(label="Notepad", command=open_txt)
popup_menu.add_command(label="Internet Explorer", command=open_internet)

popup_menu.add_separator()
popup_menu.add_command(label="Restart", command=restart_program)
popup_menu.add_command(label="Exit", command=exit_program)

# --- Icons with text ---
icons = []  # store references to prevent GC
icon_start_x, icon_start_y, icon_spacing = 20, 20, 10

def add_icon_with_label(image_path, command, text, x, y):
    try:
        icon_img = tk.PhotoImage(file=image_path)
        icons.append(icon_img)  # prevent garbage collection
        btn = tk.Button(root, image=icon_img, command=command, bd=0)
        canvas.create_window(x, y, anchor="nw", window=btn)
        lbl_y = y + icon_img.height() + 2
        lbl = tk.Label(root, text=text, bg="#008080", fg="white", font=("Helvetica", 10))
        canvas.create_window(x + icon_img.width() // 2, lbl_y, anchor="n", window=lbl)
        return icon_img.height() + lbl.winfo_reqheight() + icon_spacing
    except Exception as e:
        print(f"{text} icon not found:", e)
        return 0

icon_start_y += add_icon_with_label("SYSTEM/notepad.png", open_txt, "Notepad", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label("SYSTEM/group.png", open_game, "Games", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label("SYSTEM/player.png", open_sound, "Music", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label("SYSTEM/internet.png", open_internet, "Internet", icon_start_x, icon_start_y)

# --- Layout function ---
def draw_layout(event=None):
    canvas.delete("rect")
    width, height = canvas.winfo_width(), canvas.winfo_height()
    rect_height = 50
    canvas.create_rectangle(0, height - rect_height, width, height,
                            outline="black", width=2, fill="#818181", tags="rect")
    canvas.coords(button_window, 5, height - 5)
    canvas.coords(clock_window, width - 5, height - 5)

# --- Clock update ---
def update_time():
    clock_label.config(text=time.strftime('%H:%M:%S'))
    root.after(1000, update_time)

canvas.bind("<Configure>", draw_layout)
update_time()

# --- Right-click context menu ---
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Programs", command=None)
context_menu.add_separator()
context_menu.add_command(label="DOS Prompt", command=open_script)
context_menu.add_command(label="Games", command=open_game)
context_menu.add_command(label="Notepad", command=open_txt)
context_menu.add_command(label="Internet Explorer", command=open_internet)

root.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

root.mainloop()

