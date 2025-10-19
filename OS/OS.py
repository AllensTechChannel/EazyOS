import tkinter as tk
import time
import os
import sys
import subprocess
from tkinter import messagebox, filedialog, colorchooser
import winsound
import ctypes
from PIL import Image, ImageTk
from packaging.version import parse as parse_version

# === PATH FIX: get absolute base directory ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_icon_path(name):
    return os.path.join(BASE_DIR, "SYSTEM", name)

# --- Taskbar control (Windows only) ---
def hide_taskbar():
    taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        ctypes.windll.user32.ShowWindow(taskbar, 0)

def show_taskbar():
    taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar:
        ctypes.windll.user32.ShowWindow(taskbar, 5)

# --- Helper Commands ---
def restart_program():
    winsound.PlaySound(os.path.join(BASE_DIR, 'media', 'DING.wav'), winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)
    if messagebox.askokcancel("Restart", "Are you sure you want to restart?"):
        show_taskbar()
        root.destroy()
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "boot.py")])

def Logout_program():
    winsound.PlaySound(os.path.join(BASE_DIR, 'media', 'DING.wav'), winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)
    if messagebox.askokcancel("Logout", "Are you sure you want to log out?"):
        show_taskbar()
        root.destroy()
        winsound.PlaySound(os.path.join(BASE_DIR, 'media', 'win98logoff.wav'), winsound.SND_FILENAME)
        winsound.PlaySound(None, winsound.SND_PURGE)
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "login.py")])

def exit_program():
    winsound.PlaySound(os.path.join(BASE_DIR, 'media', 'DING.wav'), winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        winsound.PlaySound(os.path.join(BASE_DIR, 'media', 'CHIMES.wav'), winsound.SND_FILENAME)
        winsound.PlaySound(None, winsound.SND_PURGE)
        show_taskbar()
        root.destroy()
def open_personalization():
    last_color = {"value": "#008080"}
    default_taskbar_color = "#c0c0c0"

    menu = tk.Menu(root, tearoff=0)

    # --- Wallpapers ---
    wallpaper_dir = os.path.join(BASE_DIR, "media", "wallpaper")
    if not os.path.exists(wallpaper_dir):
        os.makedirs(wallpaper_dir)
    wallpapers = [f for f in os.listdir(wallpaper_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    def apply_theme(color=None, image=None, change_taskbar=True):
        """Apply desktop background (color or image)."""
        if image:
            try:
                img = Image.open(image)
                resample = Image.Resampling.LANCZOS if parse_version(Image.__version__) >= parse_version('10.0.0') else Image.ANTIALIAS
                img = img.resize((root.winfo_width(), root.winfo_height()), resample)
                bg_img = ImageTk.PhotoImage(img)
                canvas.bg_img = bg_img
                canvas.create_image(0, 0, anchor="nw", image=bg_img, tags="bg_img_tag")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set wallpaper:\n{e}")
                return
            if 'taskbar' in globals():
                taskbar.configure(bg=default_taskbar_color)
            if 'my_button' in globals():
                my_button.configure(bg=default_taskbar_color, activebackground=default_taskbar_color)
            if 'clock_label' in globals():
                clock_label.configure(bg=default_taskbar_color)
        elif color:
            if hasattr(canvas, "bg_img"):
                canvas.delete("bg_img_tag")
                del canvas.bg_img
            canvas.configure(bg=color)
            root.configure(bg=color)
            for widget in root.winfo_children():
                if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                    try:
                        widget.configure(bg=color)
                    except:
                        pass
            if change_taskbar:
                if 'taskbar' in globals():
                    taskbar.configure(bg=color)
                if 'my_button' in globals():
                    my_button.configure(bg=color, activebackground=color)
                if 'clock_label' in globals():
                    clock_label.configure(bg=color)
        else:
            messagebox.showwarning("Error", "No color or image specified")

    # --- Wallpaper menu ---
    wallpaper_menu = tk.Menu(menu, tearoff=0)
    for file in wallpapers:
        file_path = os.path.join(wallpaper_dir, file)
        wallpaper_menu.add_command(label=file, command=lambda p=file_path: apply_theme(image=p, change_taskbar=False))
    menu.add_cascade(label="Wallpapers", menu=wallpaper_menu)

    def select_from_path():
        file_path = filedialog.askopenfilename(title="Select Wallpaper", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            apply_theme(image=file_path, change_taskbar=False)
    menu.add_command(label="Select Image from Path...", command=select_from_path)
    menu.add_separator()

    def select_color():
        color = colorchooser.askcolor(title="Select Background Color")[1]
        if color:
            last_color["value"] = color
            apply_theme(color=color, change_taskbar=True)
    menu.add_command(label="Solid Color...", command=select_color)

    def reset_theme():
        if hasattr(canvas, "bg_img"):
            canvas.delete("bg_img_tag")
            del canvas.bg_img
        canvas.configure(bg="#008080")
        root.configure(bg="#008080")
        if 'taskbar' in globals():
            taskbar.configure(bg=default_taskbar_color)
        if 'my_button' in globals():
            my_button.configure(bg=default_taskbar_color, activebackground=default_taskbar_color)
        if 'clock_label' in globals():
            clock_label.configure(bg=default_taskbar_color)
        messagebox.showinfo("Reset", "Desktop reset to default Windows 98 theme!")
    menu.add_separator()
    menu.add_command(label="Reset to Default", command=reset_theme)

    x, y = root.winfo_pointerx(), root.winfo_pointery()
    menu.tk_popup(x, y)
    menu.grab_release()

# === WINDOW MANAGER ===
open_windows = []

# --- Desktop & Root Setup ---
root = tk.Tk()
root.attributes("-fullscreen", True)
root.configure(bg="#008080")
root.bind("<Escape>", lambda e: (show_taskbar(), root.destroy()))

canvas = tk.Canvas(root, bg="#008080", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# --- Taskbar ---
TASKBAR_HEIGHT = 40
TASKBAR_COLOR = "#818181"
TASKBAR_LIGHT_EDGE = "#A9A9A9"
TASKBAR_DARK_EDGE = "#5A5A5A"

# --- Start Button & Clock ---
my_button = tk.Button(root, text="Start", bg="#c3c3c3", fg="black", relief="raised", activebackground="#a0a0a0", height=1)
button_window = canvas.create_window(10, 0, anchor="w", window=my_button)

clock_label = tk.Label(root, font=("Helvetica", 10), bg=TASKBAR_COLOR, fg="Black")
clock_window = canvas.create_window(0, 0, anchor="e", window=clock_label)

def draw_taskbar(event=None):
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    if width <= 1 or height <= 1:
        return
    canvas.delete("taskbar")
    y1 = height - TASKBAR_HEIGHT
    y2 = height
    canvas.create_rectangle(0, y1, width, y2, fill=TASKBAR_COLOR, outline="", tags="taskbar")
    canvas.create_line(0, y1, width, y1, fill=TASKBAR_LIGHT_EDGE, width=2, tags="taskbar")
    canvas.create_line(0, y1, 0, y2, fill=TASKBAR_LIGHT_EDGE, width=2, tags="taskbar")
    canvas.create_line(0, y2, width, y2, fill=TASKBAR_DARK_EDGE, width=2, tags="taskbar")
    canvas.create_line(width, y1, width, y2, fill=TASKBAR_DARK_EDGE, width=2, tags="taskbar")

    button_y = y1 + TASKBAR_HEIGHT // 2
    clock_y = y1 + TASKBAR_HEIGHT // 2
    canvas.coords(button_window, 10, button_y)
    canvas.coords(clock_window, width - 10, clock_y)
    canvas.tag_raise("taskbar")
    canvas.tag_raise(button_window)
    canvas.tag_raise(clock_window)

root.bind("<Configure>", draw_taskbar)
draw_taskbar()

def update_time():
    if not root.winfo_exists():
        return
    current_time = time.strftime("%A %I:%M %p")
    clock_label.config(text=current_time)
    root.after(1000, update_time)
update_time()

# === TASKBAR WINDOW BUTTONS (with Minimize/Restore Toggle) ===
taskbar_buttons = {}
minimized_windows = set()

def add_taskbar_button(window, title):
    """Add a button for a window to the taskbar."""
    if window in taskbar_buttons:
        return

    def toggle_window():
        if window in minimized_windows:
            window.deiconify()
            window.lift()
            minimized_windows.remove(window)
            btn.config(relief="raised")
        else:
            if window.state() == "normal" and window.focus_displayof() == window:
                window.withdraw()
                minimized_windows.add(window)
                btn.config(relief="sunken")
            else:
                window.deiconify()
                window.lift()
                window.focus_force()
                minimized_windows.discard(window)
                btn.config(relief="raised")

    btn = tk.Button(
        root,
        text=title,
        bg="#C0C0C0",
        fg="black",
        relief="raised",
        activebackground="#A0A0A0",
        font=("MS Sans Serif", 9),
        padx=8,
        pady=1,
        command=toggle_window
    )

    taskbar_buttons[window] = btn
    redraw_taskbar_buttons()

def remove_taskbar_button(window):
    if window in taskbar_buttons:
        btn = taskbar_buttons.pop(window)
        btn.destroy()
        minimized_windows.discard(window)
        redraw_taskbar_buttons()

def redraw_taskbar_buttons():
    canvas.delete("taskbar_button")
    x_offset = 80
    y = canvas.winfo_height() - (TASKBAR_HEIGHT // 2)
    for btn in taskbar_buttons.values():
        canvas.create_window(x_offset, y, anchor="w", window=btn, tags="taskbar_button")
        x_offset += btn.winfo_reqwidth() + 5

# === Window Creation ===
def create_managed_window(title, script_path=None, width=600, height=400):
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry(f"{width}x{height}+100+100")
    window.configure(bg="#FAF9F6")
    window.resizable(True, True)

    open_windows.append(window)
    add_taskbar_button(window, title)
    window.protocol("WM_DELETE_WINDOW", lambda: close_window(window))

    title_bar = tk.Frame(window, bg="#000080", relief="raised", bd=1)
    title_bar.pack(fill="x")
    tk.Label(title_bar, text=title, bg="#000080", fg="white", font=("MS Sans Serif", 10, "bold")).pack(side="left", padx=5)
    tk.Button(title_bar, text="X", bg="#C0C0C0", relief="raised", width=3, command=lambda: close_window(window)).pack(side="right", padx=5)

    content_frame = tk.Frame(window, bg="#FAF9F6")
    content_frame.pack(fill="both", expand=True)
    tk.Label(content_frame, text=f"{title} is running...", bg="#FAF9F6").pack(pady=50)

    if script_path and os.path.exists(script_path):
        subprocess.Popen([sys.executable, script_path])
    elif script_path:
        tk.Label(content_frame, text=f"Script not found:\n{script_path}", fg="red", bg="#FAF9F6").pack(pady=20)

    def start_move(event): window.x = event.x; window.y = event.y
    def stop_move(event): window.x = None; window.y = None
    def do_move(event):
        x = window.winfo_x() + (event.x - window.x)
        y = window.winfo_y() + (event.y - window.y)
        window.geometry(f"+{x}+{y}")

    title_bar.bind("<ButtonPress-1>", start_move)
    title_bar.bind("<ButtonRelease-1>", stop_move)
    title_bar.bind("<B1-Motion>", do_move)
    window.bind("<Button-1>", lambda e: window.lift())
    return window

def close_window(window):
    if window in open_windows:
        open_windows.remove(window)
    remove_taskbar_button(window)
    window.destroy()

# --- Program Shortcuts ---
def open_txt(): create_managed_window("Notepad", os.path.join(BASE_DIR, "..", "Program Files","notepad", "notepad.py"))
def open_game(): create_managed_window("Games", os.path.join(BASE_DIR, "Program Files", "Games", "select.py"))
def open_sound(): create_managed_window("Music Player", os.path.join(BASE_DIR, "Program Files", "Sound Player", "music_player.py"))
def open_internet(): create_managed_window("Internet Explorer", os.path.join(BASE_DIR, "internet explorer", "select.py"))

def open_about(): create_managed_window("About EazyOS", os.path.join(BASE_DIR, "about.py"))
def open_file(): create_managed_window("File Explorer", os.path.join(BASE_DIR, "..","Program Files","file","src","main.py"))
def open_script(): create_managed_window("DOS Prompt", os.path.join(BASE_DIR, "SYSTEM", "CMD.py"))
def open_saver1(): create_managed_window("Bubbles Screensaver", os.path.join(BASE_DIR, "..","Program Files", "screensaver","bubbles.py"))
def open_saver2():
    saver_dir = os.path.join(BASE_DIR, "..", "Program Files", "screensaver")
    main_script = os.path.join(saver_dir, "main.py")
    if not os.path.exists(saver_dir):
        os.makedirs(saver_dir)
    create_managed_window("DVD Screensaver", main_script)

# --- Desktop Icons ---
icons = []
icon_start_x, icon_start_y, icon_spacing = 20, 20, 10

def add_icon_with_label(image_path, command, text, x, y):
    try:
        icon_img = tk.PhotoImage(file=image_path)
        icons.append(icon_img)
        btn = tk.Button(root, image=icon_img, command=command, bd=0, bg="#008080", activebackground="#008080")
        canvas.create_window(x, y, anchor="nw", window=btn)
        lbl_y = y + icon_img.height() + 2
        lbl = tk.Label(root, text=text, bg="#008080", fg="white", font=("MS Sans Serif", 9))
        canvas.create_window(x + icon_img.width() // 2, lbl_y, anchor="n", window=lbl)
        return icon_img.height() + lbl.winfo_reqheight() + icon_spacing
    except Exception as e:
        print(f"{text} icon not found:", e)
        return 0

icon_start_y += add_icon_with_label(get_icon_path("notepad.png"), open_txt, "Notepad", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label(get_icon_path("group.png"), open_game, "Games", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label(get_icon_path("player.png"), open_sound, "Music", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label(get_icon_path("internet.png"), open_internet, "Internet", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label(get_icon_path("display_properties.png"), open_personalization, "Display", icon_start_x, icon_start_y)
icon_start_y += add_icon_with_label(get_icon_path("explorer.png"), open_file, "Explorer", icon_start_x, icon_start_y)

# --- Start Menu ---
popup_menu = tk.Menu(root, tearoff=0)
popup_menu.add_command(label="EazyOS", command=None)
popup_menu.add_separator()
popup_menu.add_command(label="About EazyOS", command=open_about)
popup_menu.add_separator()
programs_menu = tk.Menu(popup_menu, tearoff=0)
programs_menu.add_command(label="Notepad", command=open_txt)
programs_menu.add_command(label="Games", command=open_game)
programs_menu.add_command(label="Music Player", command=open_sound)
programs_menu.add_command(label="Internet Explorer", command=open_internet)
programs_menu.add_command(label="DOS Prompt", command=open_script)
programs_menu.add_command(label="File Explorer", command=open_file)
popup_menu.add_cascade(label="Programs", menu=programs_menu)
popup_menu.add_separator()
personalization_menu = tk.Menu(popup_menu, tearoff=0)
personalization_menu.add_command(label="Wallpapers & Colors", command=open_personalization)
popup_menu.add_cascade(label="Personalization", menu=personalization_menu)
screensaver_menu = tk.Menu(popup_menu, tearoff=0)
screensaver_menu.add_command(label="Bubbles", command=open_saver1)
screensaver_menu.add_command(label="DVD", command=open_saver2)
popup_menu.add_cascade(label="Screensaver", menu=screensaver_menu)
popup_menu.add_separator()
popup_menu.add_command(label="Restart", command=restart_program)
popup_menu.add_command(label="Exit", command=exit_program)
popup_menu.add_command(label="Logout", command=Logout_program)
my_button.config(command=lambda: popup_menu.tk_popup(5, root.winfo_height() - TASKBAR_HEIGHT))

# --- Right-Click Context Menu ---
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Programs")
context_menu.add_separator()
context_menu.add_command(label="DOS Prompt", command=open_script)
context_menu.add_command(label="Games", command=open_game)
context_menu.add_command(label="Notepad", command=open_txt)
context_menu.add_command(label="Internet Explorer", command=open_internet)
context_menu.add_command(label="File Explorer", command=open_file)
context_menu.add_separator()
context_menu.add_command(label="Personalization", command=open_personalization)
root.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

# --- Startup Sound ---
winsound.PlaySound(os.path.join(BASE_DIR, 'media', 'The Microsoft Sound.wav'), winsound.SND_FILENAME)
winsound.PlaySound(None, winsound.SND_PURGE)

root.mainloop()
