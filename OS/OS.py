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

# === PATH FIX ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_bat_in_terminal(bat_path):
    win = create_managed_window("Command Prompt", width=700, height=500)

    # Create terminal display
    text_widget = tk.Text(win, bg="black", fg="white", insertbackground="white",
                          font=("Consolas", 10))
    text_widget.pack(fill="both", expand=True)

    text_widget.insert("end", f"Executing {os.path.basename(bat_path)}...\n\n")
    text_widget.see("end")

    # Run BAT file using cmd.exe
    def run():
        process = subprocess.Popen(
            ['cmd.exe', '/c', bat_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )

        # Stream output live
        for line in process.stdout:
            text_widget.insert("end", line)
            text_widget.see("end")

        for line in process.stderr:
            text_widget.insert("end", line)
            text_widget.see("end")

        text_widget.insert("end", "\nProcess finished.\n")
        text_widget.see("end")

    root.after(50, run)

def get_icon_path(name):
    return os.path.join(BASE_DIR, "media","icons", name)


# === TASKBAR HIDE / SHOW ===
def hide_taskbar():
    taskbar_hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar_hwnd:
        ctypes.windll.user32.ShowWindow(taskbar_hwnd, 0)


def show_taskbar():
    taskbar_hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if taskbar_hwnd:
        ctypes.windll.user32.ShowWindow(taskbar_hwnd, 5)


# === WINDOW MANAGER ===
open_windows = []
minimized_windows = set()
taskbar_buttons = {}


# === ROOT SETUP ===
root = tk.Tk()
root.title("EazyOS-Desktop")
root.attributes("-fullscreen", True)
root.configure(bg="#008080")
root.bind("<Escape>", lambda e: (show_taskbar(), root.destroy()))

canvas = tk.Canvas(root, bg="#008080", highlightthickness=0)
canvas.pack(fill="both", expand=True)
taskbar = canvas      # <-- FIXED: taskbar is now defined
import os


# Specify the file path
file_path = 'bios.py'



if os.path.exists(file_path):
    print("The file", file_path, "exists.")
else:
    messagebox.showwarning(
        "System file not found",
        f"The system file {file_path} does not exist."
    )
file_path = 'bsod.py'



if os.path.exists(file_path):
    print("The file", file_path, "exists.")
else:
    messagebox.showwarning(
        "System file not found",
        f"The system file {file_path} does not exist."
    )
    
file_path = 'SYSTEM'



if os.path.exists(file_path):
    print("The file", file_path, "exists.")
else:
    messagebox.showwarning(
        "System file not found",
        f"The system file {file_path} does not exist."
    )
   

# === SOUND HELPERS ===
def play_sound(path):
    winsound.PlaySound(path, winsound.SND_FILENAME)
    winsound.PlaySound(None, winsound.SND_PURGE)


# === HELPER COMMANDS ===
def restart_program():
    play_sound(os.path.join('media', 'DING.wav'))
    if messagebox.askokcancel("Restart", "Are you sure you want to restart?"):
        show_taskbar()
        root.destroy()
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "boot.py")])


def Logout_program():
    play_sound(os.path.join('media', 'DING.wav'))
    if messagebox.askokcancel("Logout", "Are you sure you want to log out?"):
        show_taskbar()
        root.destroy()
        play_sound(os.path.join(BASE_DIR, 'media', 'win98logoff.wav'))
        subprocess.run([sys.executable, os.path.join(BASE_DIR, "login.py")])


def exit_program():
    play_sound(os.path.join('media', 'DING.wav'))
    if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
        play_sound(os.path.join(BASE_DIR, 'media', 'CHIMES.wav'))
        show_taskbar()
        root.destroy()
# === PERSONALIZATION MENU ===
def open_personalization():
    last_color = {"value": "#008080"}
    default_taskbar_color = "#c0c0c0"

    def apply_theme(color=None, image=None):
        """Apply desktop background (color or image)."""
        if image:
            try:
                img = Image.open(image)
                resample = Image.Resampling.LANCZOS if parse_version(Image.__version__) >= parse_version("10.0.0") else Image.ANTIALIAS
                img = img.resize((root.winfo_width(), root.winfo_height()), resample)
                bg_img = ImageTk.PhotoImage(img)
                canvas.bg_img = bg_img
                canvas.create_image(0, 0, anchor="nw", image=bg_img, tags="desktop_bg")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set wallpaper:\n{e}")
                return

            # Reset taskbar
            taskbar.configure(bg=default_taskbar_color)
            clock_label.configure(bg=default_taskbar_color)
            my_button.configure(bg=default_taskbar_color, activebackground=default_taskbar_color)
            return

        if color:
            canvas.delete("desktop_bg")
            canvas.configure(bg=color)
            root.configure(bg=color)
            taskbar.configure(bg=color)
            my_button.configure(bg=color, activebackground=color)
            clock_label.configure(bg=color)

    # --- Wallpaper menu ---
    wallpaper_menu = tk.Menu(root, tearoff=0, bg="white", fg="black",
                             activebackground="#000080", activeforeground="white")

    # Solid color option
    def pick_color():
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            last_color["value"] = color
            apply_theme(color=color)
    wallpaper_menu.add_command(label="Solid Color", command=pick_color)

    # Default backgrounds submenu
    wallpaper_submenu = tk.Menu(wallpaper_menu, tearoff=0, bg="white", fg="black",
                                activebackground="#000080", activeforeground="white")
    wallpaper_dir = os.path.join(BASE_DIR, "media", "wallpaper")
    os.makedirs(wallpaper_dir, exist_ok=True)

    # Add all images in the folder
    for file in os.listdir(wallpaper_dir):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            path = os.path.join(wallpaper_dir, file)
            wallpaper_submenu.add_command(
                label=file,
                command=lambda p=path: apply_theme(image=p)
            )

    wallpaper_menu.add_cascade(label="Default Backgrounds", menu=wallpaper_submenu)

    # Select custom wallpaper
    def select_custom_wallpaper():
        file_path = filedialog.askopenfilename(
            title="Select Wallpaper",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            apply_theme(image=file_path)
    wallpaper_menu.add_command(label="Select From File...", command=select_custom_wallpaper)
    wallpaper_menu.add_separator()

    # Reset to default
    def reset_theme():
        canvas.delete("desktop_bg")
        canvas.configure(bg="#008080")
        root.configure(bg="#008080")
        taskbar.configure(bg=default_taskbar_color)
        my_button.configure(bg=default_taskbar_color)
        clock_label.configure(bg=default_taskbar_color)
        messagebox.showinfo("Reset", "Theme reset to Windows 98 default.")
    wallpaper_menu.add_command(label="Reset to Default", command=reset_theme)

    # Show the wallpaper menu at mouse position
    try:
        wallpaper_menu.tk_popup(root.winfo_pointerx(), root.winfo_pointery())
    finally:
        wallpaper_menu.grab_release()





# === TASKBAR RENDERING ===
TASKBAR_HEIGHT = 40
TASKBAR_COLOR = "#818181"
TASKBAR_LIGHT = "#A9A9A9"
TASKBAR_DARK = "#5A5A5A"

my_button = tk.Button(root, text="Start", bg="#c3c3c3", fg="black", relief="raised")
button_window = canvas.create_window(10, 0, anchor="w", window=my_button)

clock_label = tk.Label(root, font=("Helvetica", 10), bg=TASKBAR_COLOR, fg="Black")
clock_window = canvas.create_window(0, 0, anchor="e", window=clock_label)


def draw_taskbar(event=None):
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w <= 1 or h <= 1:
        return

    canvas.delete("taskbar")
    y1 = h - TASKBAR_HEIGHT
    y2 = h

    # Main taskbar rectangle
    canvas.create_rectangle(0, y1, w, y2, fill=TASKBAR_COLOR, outline="", tags="taskbar")

    # Edges
    canvas.create_line(0, y1, w, y1, fill=TASKBAR_LIGHT, width=2, tags="taskbar")
    canvas.create_line(0, y2, w, y2, fill=TASKBAR_DARK, width=2, tags="taskbar")

    # Position buttons
    canvas.coords(button_window, 10, y1 + TASKBAR_HEIGHT // 2)
    canvas.coords(clock_window, w - 10, y1 + TASKBAR_HEIGHT // 2)

    canvas.tag_raise(button_window)
    canvas.tag_raise(clock_window)


root.bind("<Configure>", draw_taskbar)
draw_taskbar()


# === CLOCK ===
def update_time():
    if root.winfo_exists():
        clock_label.config(text=time.strftime("%A %I:%M %p"))
        root.after(1000, update_time)


update_time()


# === TASKBAR WINDOW BUTTONS ===
def redraw_taskbar_buttons():
    canvas.delete("taskbar_button")

    x = 80
    y = canvas.winfo_height() - (TASKBAR_HEIGHT // 2)

    for btn in taskbar_buttons.values():
        canvas.create_window(x, y, anchor="w", window=btn, tags="taskbar_button")
        x += btn.winfo_reqwidth() + 5


def add_taskbar_button(window, title):
    if window in taskbar_buttons:
        return

    def toggle():
        if window in minimized_windows:
            window.deiconify()
            window.lift()
            minimized_windows.remove(window)
            btn.config(relief="raised")
        else:
            if window.state() == "normal":
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
        command=toggle
    )

    taskbar_buttons[window] = btn
    redraw_taskbar_buttons()


def remove_taskbar_button(window):
    if window in taskbar_buttons:
        taskbar_buttons[window].destroy()
        taskbar_buttons.pop(window)
        minimized_windows.discard(window)
        redraw_taskbar_buttons()


# === WINDOW CREATION ===
def close_window(window):
    if window in open_windows:
        open_windows.remove(window)
    remove_taskbar_button(window)
    window.destroy()


def create_managed_window(title, script=None, width=600, height=400):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry(f"{width}x{height}+100+100")
    win.configure(bg="#FAF9F6")

    open_windows.append(win)
    add_taskbar_button(win, title)

    win.protocol("WM_DELETE_WINDOW", lambda: close_window(win))

    # Title bar
    bar = tk.Frame(win, bg="#000080")
    bar.pack(fill="x")

    tk.Label(bar, text=title, bg="#000080", fg="white",
             font=("MS Sans Serif", 10, "bold")).pack(side="left", padx=5)

    tk.Button(bar, text="X", width=3, bg="#C0C0C0",
              command=lambda: close_window(win)).pack(side="right", padx=5)

    # Content
    body = tk.Frame(win, bg="#FAF9F6")
    body.pack(fill="both", expand=True)

    tk.Label(body, text=f"{title} is running...", bg="#FAF9F6").pack(pady=50)

    if script and os.path.exists(script):
        subprocess.Popen([sys.executable, script])
    elif script:
        tk.Label(body, text=f"Script missing:\n{script}", fg="red", bg="#FAF9F6").pack()

    # Dragging
    def start(e): win.x = e.x; win.y = e.y
    def drag(e):
        win.geometry(f"+{win.winfo_x() + (e.x - win.x)}+{win.winfo_y() + (e.y - win.y)}")

    bar.bind("<ButtonPress-1>", start)
    bar.bind("<B1-Motion>", drag)

    win.bind("<Button-1>", lambda e: win.lift())

    return win


# === DESKTOP ICONS ===
icons = []
icon_spacing = 20
icon_start_x = 20
icon_start_y = 20


def add_icon(image, cmd, text, x, y):
    try:
        img = tk.PhotoImage(file=image)
        icons.append(img)

        btn = tk.Button(root, image=img, command=cmd, bd=0,
                        bg="#008080", activebackground="#008080")

        canvas.create_window(x, y, anchor="nw", window=btn)

        lbl_y = y + img.height() + 2
        lbl = tk.Label(root, text=text, bg="#008080", fg="white",
                       font=("MS Sans Serif", 9))

        canvas.create_window(x + img.width() // 2, lbl_y, anchor="n", window=lbl)

        return img.height() + 20

    except Exception as e:
        print(f"Missing icon {text}:", e)
        return 40
# === PROGRAM SHORTCUTS ===
def open_txt():
    create_managed_window("Notepad", os.path.join(BASE_DIR, "..", "Program Files", "notepad", "notepad.py"))
def open_calc():
    create_managed_window("Calculator", os.path.join(BASE_DIR, "..", "Program Files", "calc", "calc.py"))
def open_paint():
    create_managed_window("Paint", os.path.join(BASE_DIR, "..", "Program Files", "paint", "main.py"))

def open_update():
    if messagebox.askyesno("Update", "Are you sure you want to upgrade?"):
        create_managed_window("Update", os.path.join(BASE_DIR,"setup","UPDATEOS.py"))

def open_game(): create_managed_window("Games", os.path.join(BASE_DIR,"..", "Program Files", "Games", "select.py"))
def open_sound():
    create_managed_window("Music Player", os.path.join(BASE_DIR, "..", "Program Files", "Sound Playe", "music_player.py"))

def open_internet():
    create_managed_window("Internet Explorer", os.path.join(BASE_DIR, "internet explorer", "select.py"))

def open_taskmgr():
    create_managed_window("Task Manager", os.path.join(BASE_DIR, "SYSTEM", "taskmgr.py"))

def bsod():
    create_managed_window("BSOD", os.path.join(BASE_DIR, "BSOD.py"))

def open_about():
    create_managed_window("About EazyOS", os.path.join(BASE_DIR, "SYSTEM", "about.py"))
def open_alarm():
    create_managed_window("Alarm", os.path.join(BASE_DIR,"..","Program Files", "alarm", "alarm.py"))

def user():
    bat_path = os.path.join(BASE_DIR, "system","User.bat")
    if not os.path.exists(bat_path):
        messagebox.showerror("Error", "User.bat not found!")
        return

    run_bat_in_terminal(bat_path)



def open_file():
    create_managed_window("File Explorer", os.path.join(BASE_DIR, "..", "Program Files", "file", "src", "main.py"))

def open_script():
    create_managed_window("DOS Prompt", os.path.join(BASE_DIR, "SYSTEM", "CMD.py"))

def open_saver1():
    create_managed_window("Bubbles Screensaver", os.path.join(BASE_DIR, "..", "Program Files", "screensaver", "bubbles.py"))

def open_saver2():
    saver_dir = os.path.join(BASE_DIR, "..", "Program Files", "screensaver")
    main_script = os.path.join(saver_dir, "main.py")
    os.makedirs(saver_dir, exist_ok=True)
    create_managed_window("DVD Screensaver", main_script)


# === ADD DESKTOP ICONS ===
icon_start_y += add_icon(get_icon_path("notepad.png"), open_txt, "Notepad", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("group.png"), open_game, "Games", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("player.png"), open_sound, "Music", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("internet.png"), open_internet, "Internet", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("display_properties.png"), open_personalization, "Display", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("explorer.png"), open_file, "Explorer", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("calc.png"), open_calc, "Calculator", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("paint.png"), open_paint, "Paint", icon_start_x, icon_start_y)
icon_start_y += add_icon(get_icon_path("clock.png"), open_alarm, "Alarm", icon_start_x, icon_start_y)


# === START MENU ===

popup_menu = tk.Menu(
    root,
    tearoff=0,
    bg="white",
    fg="black",
    activebackground="#000080",
    activeforeground="white"
)

popup_menu.add_command(label="EazyOS 3")
popup_menu.add_separator()
popup_menu.add_command(label="About EazyOS", command=open_about)
popup_menu.add_command(label="Update EazyOS", command=open_update)
popup_menu.add_separator()

programs = tk.Menu(
    popup_menu,
    tearoff=0,
    bg="white",
    fg="black",
    activebackground="#000080",
    activeforeground="white"
)

programs.add_command(label="Notepad", command=open_txt)
programs.add_command(label="Games", command=open_game)
programs.add_command(label="Music Player", command=open_sound)
programs.add_command(label="Internet Explorer", command=open_internet)
programs.add_command(label="DOS Prompt", command=open_script)
programs.add_command(label="File Explorer", command=open_file)
programs.add_command(label="Paint", command=open_paint)
programs.add_command(label="Calculator", command=open_calc)
programs.add_command(label="Alarm", command=open_alarm)


popup_menu.add_cascade(label="Programs", menu=programs)

popup_menu.add_separator()

personal = tk.Menu(
    popup_menu,
    tearoff=0,
    bg="white",
    fg="black",
    activebackground="#000080",
    activeforeground="white"
)

personal.add_command(label="Wallpapers, Colors, Settings", command=open_personalization)
popup_menu.add_cascade(label="Personalization", menu=personal)

popup_menu.add_command(label="Add Username and Password", command=user)

screensaver = tk.Menu(
    popup_menu,
    tearoff=0,
    bg="white",
    fg="black",
    activebackground="#000080",
    activeforeground="white"
)

screensaver.add_command(label="Bubbles", command=open_saver1)
screensaver.add_command(label="DVD", command=open_saver2)

popup_menu.add_cascade(label="Screensaver", menu=screensaver)

popup_menu.add_separator()
popup_menu.add_command(label="Restart", command=restart_program)
popup_menu.add_command(label="Exit", command=exit_program)
popup_menu.add_command(label="Logout", command=Logout_program)

my_button.config(command=lambda: popup_menu.tk_popup(5, root.winfo_height() - TASKBAR_HEIGHT))

# === RIGHT-CLICK DESKTOP MENU ===


right_click_menu = tk.Menu(
    root,
    tearoff=0,
    bg="white",
    fg="black",
    activebackground="#000080",
    activeforeground="white"
)
right_click_menu.add_command(label="Notepad", command=open_txt)
right_click_menu.add_command(label="Games", command=open_game)
right_click_menu.add_command(label="Internet Explorer", command=open_internet)
right_click_menu.add_command(label="File Explorer", command=open_file)
right_click_menu.add_command(label="Calculator", command=open_calc)
right_click_menu.add_command(label="Paint", command=open_paint)
right_click_menu.add_separator()
right_click_menu.add_command(label="Personalization", command=open_personalization)

root.bind("<Button-3>", lambda e: right_click_menu.post(e.x_root, e.y_root))


# === STARTUP SOUND ===
play_sound(os.path.join(BASE_DIR, 'media', 'The Microsoft Sound.wav'))


# === BSOD SHORTCUT ===
def trigger_bsod_and_exit():
    bsod()
    root.after(500, root.destroy)   # FIX: give BSOD time to appear

root.bind("<Control-Shift-B>", lambda e: trigger_bsod_and_exit())


# === OPTIONAL: CTRL + ALT + BACKSPACE for task manager ===
def on_key(event):
    ctrl = event.state & 0x4
    alt = event.state & 0x20000
    if ctrl and alt and event.keysym.lower() == "backspace":
        open_taskmgr()

root.bind("<Key>", on_key)


# === RUN THE OS ===
root.mainloop()

