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
from typing import Optional, Callable, Dict, Set
import logging
import json
import datetime

# Target date for event
target_date = datetime.datetime(2036, 2, 16, 0, 0, 0)

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eazyos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === PATH CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join("media")
ICONS_DIR = os.path.join(MEDIA_DIR, "icons")
WALLPAPER_DIR = os.path.join(MEDIA_DIR, "wallpaper")
PROGRAM_FILES_DIR = os.path.join(BASE_DIR, "..", "Program Files")
SYSTEM_DIR = os.path.join(BASE_DIR, "SYSTEM")
CONFIG_FILE = os.path.join(BASE_DIR, "eazyos_config.json")

# === CONSTANTS ===
TASKBAR_HEIGHT = 40
TASKBAR_COLOR = "#c0c0c0"
TASKBAR_LIGHT = "#A9A9A9"
TASKBAR_DARK = "#5A5A5A"
DEFAULT_BG_COLOR = "#008080"
DESKTOP_FG_COLOR = "white"
WIN98_BLUE = "#000080"

# === CONFIGURATION ===
HIDE_WINDOWS_TASKBAR = False
DEBUG_THEME_LOADING = False
ENABLE_SOUNDS = True


class ConfigManager:
    """Manages saving and loading configuration settings"""

    DEFAULT_CONFIG = {
        "theme": {
            "type": "color",
            "color": DEFAULT_BG_COLOR,
            "wallpaper": None,
            "taskbar_color": "#c0c0c0",
            "window_title_color": "#000080",
        },
        "system": {
            "startup_sound": "true",
            "enable_sounds": "true",
            "show_clock": "true",
            "auto_hide_windows_taskbar": "true",
        }
    }

    @staticmethod
    def load_config() -> dict:
        import copy
        default_config = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
        try:
            logger.info(f"Looking for config file at: {CONFIG_FILE}")
            if os.path.exists(CONFIG_FILE):
                logger.info(f"Config file found, loading...")
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    for section, defaults in default_config.items():
                        if section not in config:
                            config[section] = defaults
                        elif isinstance(defaults, dict):
                            for k, v in defaults.items():
                                config[section].setdefault(k, v)
                    logger.info(f"Loaded configuration: {config}")
                    return config
            else:
                logger.info(f"Config file not found, using default")
        except Exception as e:
            logger.error(f"Failed to load config: {e}", exc_info=True)
        return default_config

    @staticmethod
    def save_config(config: dict) -> bool:
        try:
            logger.info(f"Saving config to: {CONFIG_FILE}")
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Successfully saved configuration")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}", exc_info=True)
            return False

    @staticmethod
    def get_system(config: dict) -> dict:
        return config.get("system", ConfigManager.DEFAULT_CONFIG["system"])

    @staticmethod
    def bool_val(config: dict, section: str, key: str, default: bool = True) -> bool:
        raw = config.get(section, {}).get(key, str(default)).lower()
        return raw in ("true", "1", "yes")


class SoundManager:
    """Centralized sound management"""

    @staticmethod
    def play(filename: str, async_play: bool = True) -> None:
        if not ENABLE_SOUNDS:
            return
        try:
            path = os.path.join(MEDIA_DIR, filename)
            if os.path.exists(path):
                flags = winsound.SND_FILENAME | winsound.SND_NODEFAULT
                if async_play:
                    flags |= winsound.SND_ASYNC
                winsound.PlaySound(path, flags)
                logger.info(f"Playing sound: {filename}")
            else:
                logger.warning(f"Sound file not found: {path}")
        except Exception as e:
            logger.error(f"Failed to play sound {filename}: {e}")

    @staticmethod
    def stop() -> None:
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception as e:
            logger.error(f"Failed to stop sound: {e}")


class TaskbarManager:
    """Manages the Windows taskbar visibility"""

    def __init__(self, hwnd, auto_hide=False):
        self.hwnd = hwnd
        self._hidden = False
        self._auto_hide = auto_hide

    def hide(self) -> None:
        if not self._auto_hide:
            return
        try:
            if self.hwnd and not self._hidden:
                ctypes.windll.user32.ShowWindow(self.hwnd, 0)
                self._hidden = True
                logger.info("Windows taskbar hidden")
        except Exception as e:
            logger.error(f"Failed to hide taskbar: {e}")

    def show(self) -> None:
        try:
            if self.hwnd:
                ctypes.windll.user32.ShowWindow(self.hwnd, 5)
                self._hidden = False
                logger.info("Windows taskbar restored")
        except Exception as e:
            logger.error(f"Failed to show taskbar: {e}")


class WindowManager:
    """Manages application windows and taskbar buttons"""

    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        self.open_windows: list = []
        self.minimized_windows: Set = set()
        self.taskbar_buttons: Dict = {}

    def create_window(self, title: str, script: Optional[str] = None,
                      width: int = 600, height: int = 400) -> tk.Toplevel:
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry(f"{width}x{height}+100+100")
        win.configure(bg="#FAF9F6")

        self.open_windows.append(win)
        self._add_taskbar_button(win, title)
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_window(win))
        self._create_title_bar(win, title)

        body = tk.Frame(win, bg="#FAF9F6")
        body.pack(fill="both", expand=True, padx=2, pady=2)

        if script:
            self._launch_script(win, body, script)

        win.bind("<Button-1>", lambda e: win.lift())
        return win

    def _create_title_bar(self, win: tk.Toplevel, title: str) -> None:
        bar = tk.Frame(win, bg=WIN98_BLUE, height=25)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        title_label = tk.Label(bar, text=title, bg=WIN98_BLUE, fg="white",
                               font=("MS Sans Serif", 9, "bold"))
        title_label.pack(side="left", padx=5, pady=2)

        close_btn = tk.Button(bar, text="✕", width=3, bg=TASKBAR_COLOR,
                              font=("MS Sans Serif", 8, "bold"), relief="raised", bd=1,
                              command=lambda: self._close_window(win))
        close_btn.pack(side="right", padx=2, pady=2)

        min_btn = tk.Button(bar, text="_", width=3, bg=TASKBAR_COLOR,
                            font=("MS Sans Serif", 8, "bold"), relief="raised", bd=1,
                            command=lambda: self._minimize_window(win))
        min_btn.pack(side="right", padx=0, pady=2)

        self._make_draggable(win, bar)
        self._make_draggable(win, title_label)

    def _make_draggable(self, window: tk.Toplevel, widget: tk.Widget) -> None:
        def start_drag(event):
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y

        def drag(event):
            x = window.winfo_x() + (event.x - widget._drag_start_x)
            y = window.winfo_y() + (event.y - widget._drag_start_y)
            window.geometry(f"+{x}+{y}")

        widget.bind("<ButtonPress-1>", start_drag)
        widget.bind("<B1-Motion>", drag)

    def _minimize_window(self, window: tk.Toplevel) -> None:
        window.withdraw()
        self.minimized_windows.add(window)
        if window in self.taskbar_buttons:
            self.taskbar_buttons[window].config(relief="sunken")

    def _close_window(self, window: tk.Toplevel) -> None:
        if window in self.open_windows:
            self.open_windows.remove(window)
        self._remove_taskbar_button(window)
        try:
            window.destroy()
        except Exception as e:
            logger.error(f"Error closing window: {e}")

    def _launch_script(self, window: tk.Toplevel, body: tk.Frame, script: str) -> None:
        if not os.path.exists(script):
            tk.Label(body, text=f"Script not found:\n{script}", fg="red",
                     bg="#FAF9F6", font=("MS Sans Serif", 10)).pack(pady=50)
            logger.error(f"Script not found: {script}")
            return
        try:
            subprocess.Popen([sys.executable, script])
            tk.Label(body, text=f"{window.title()} launched successfully",
                     bg="#FAF9F6", font=("MS Sans Serif", 10)).pack(pady=50)
        except Exception as e:
            tk.Label(body, text=f"Failed to launch:\n{str(e)}", fg="red",
                     bg="#FAF9F6", font=("MS Sans Serif", 10)).pack(pady=50)
            logger.error(f"Failed to launch script {script}: {e}")

    def _add_taskbar_button(self, window: tk.Toplevel, title: str) -> None:
        if window in self.taskbar_buttons:
            return

        def toggle():
            if window in self.minimized_windows:
                window.deiconify()
                window.lift()
                window.focus_force()
                self.minimized_windows.remove(window)
                btn.config(relief="raised")
            else:
                if window.state() == "normal":
                    self._minimize_window(window)
                else:
                    window.deiconify()
                    window.lift()
                    window.focus_force()
                    self.minimized_windows.discard(window)
                    btn.config(relief="raised")

        btn = tk.Button(self.root, text=title[:20], bg=TASKBAR_COLOR, fg="black",
                        relief="raised", activebackground="#A0A0A0",
                        font=("MS Sans Serif", 9), padx=8, pady=2, command=toggle)

        self.taskbar_buttons[window] = btn
        self._redraw_taskbar_buttons()

    def _remove_taskbar_button(self, window: tk.Toplevel) -> None:
        if window in self.taskbar_buttons:
            self.taskbar_buttons[window].destroy()
            self.taskbar_buttons.pop(window)
            self.minimized_windows.discard(window)
            self._redraw_taskbar_buttons()

    def _redraw_taskbar_buttons(self) -> None:
        self.canvas.delete("taskbar_button")
        x = 80
        y = self.canvas.winfo_height() - (TASKBAR_HEIGHT // 2)
        for btn in self.taskbar_buttons.values():
            self.canvas.create_window(x, y, anchor="w", window=btn, tags="taskbar_button")
            x += btn.winfo_reqwidth() + 5


class ThemeManager:
    """Manages desktop themes and wallpapers"""

    def __init__(self, root, canvas, taskbar_widgets, show_error_callback=None):
        self.root = root
        self.canvas = canvas
        self.taskbar_widgets = taskbar_widgets
        self.current_wallpaper = None
        self.show_error = show_error_callback or (lambda msg: messagebox.showerror("Error", msg))
        self.config = ConfigManager.load_config()

    def apply_theme(self, color: Optional[str] = None, image_path: Optional[str] = None, save: bool = True) -> None:
        if image_path:
            self._apply_wallpaper(image_path)
            if save:
                self.config["theme"].update({"type": "wallpaper", "color": None, "wallpaper": image_path})
                ConfigManager.save_config(self.config)
        elif color:
            self._apply_color(color)
            if save:
                self.config["theme"].update({"type": "color", "color": color, "wallpaper": None})
                ConfigManager.save_config(self.config)

    def apply_from_config(self) -> None:
        self.config = ConfigManager.load_config()
        theme = self.config.get("theme", {})

        theme_type = theme.get("type", "color")
        if theme_type == "wallpaper" and theme.get("wallpaper"):
            wp = theme["wallpaper"]
            if os.path.exists(wp):
                self._apply_wallpaper(wp)
            else:
                self._apply_color(theme.get("color") or DEFAULT_BG_COLOR)
        else:
            self._apply_color(theme.get("color") or DEFAULT_BG_COLOR)

        taskbar_color = theme.get("taskbar_color", TASKBAR_COLOR)
        for widget in self.taskbar_widgets:
            try:
                widget.configure(bg=taskbar_color)
            except Exception:
                pass

        win_title_color = theme.get("window_title_color", WIN98_BLUE)
        for win in self.root.winfo_children():
            if isinstance(win, tk.Toplevel):
                for child in win.winfo_children():
                    if isinstance(child, tk.Frame) and child.cget("bg") == WIN98_BLUE:
                        child.configure(bg=win_title_color)

        logger.info(f"apply_from_config: type={theme_type}, taskbar={taskbar_color}, "
                    f"title_bar={win_title_color}")

    def _apply_wallpaper(self, image_path: str) -> None:
        try:
            img = Image.open(image_path)
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            resample = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
            img = img.resize((width, height), resample)
            bg_img = ImageTk.PhotoImage(img)
            self.canvas.bg_img = bg_img
            self.canvas.delete("desktop_bg")
            self.canvas.create_image(0, 0, anchor="nw", image=bg_img, tags="desktop_bg")
            self.canvas.tag_lower("desktop_bg")
            self._reset_taskbar_colors()
            logger.info(f"Applied wallpaper: {image_path}")
        except Exception as e:
            logger.error(f"Failed to apply wallpaper {image_path}: {e}")
            self.show_error(f"Failed to set wallpaper:\n{e}")

    def _apply_color(self, color: str) -> None:
        self.canvas.delete("desktop_bg")
        self.canvas.configure(bg=color)
        self.root.configure(bg=color)
        for widget in self.taskbar_widgets:
            widget.configure(bg=color)
        self.canvas.tag_raise("taskbar")
        self.canvas.tag_raise("taskbar_button")
        logger.info(f"Applied background color: {color}")

    def _reset_taskbar_colors(self) -> None:
        for widget in self.taskbar_widgets:
            widget.configure(bg=TASKBAR_COLOR)

    def reset_to_default(self) -> None:
        self.canvas.delete("desktop_bg")
        self.canvas.configure(bg=DEFAULT_BG_COLOR)
        self.root.configure(bg=DEFAULT_BG_COLOR)
        self._reset_taskbar_colors()
        self.config["theme"] = {"type": "color", "color": DEFAULT_BG_COLOR, "wallpaper": None}
        ConfigManager.save_config(self.config)
        logger.info("Theme reset to default")

    def load_saved_theme(self) -> None:
        try:
            logger.info("Loading saved theme...")
            self.apply_from_config()
        except Exception as e:
            logger.error(f"Failed to load saved theme: {e}", exc_info=True)
            self.apply_theme(color=DEFAULT_BG_COLOR, save=False)


class EazyOSDesktop:
    """Main desktop application class"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EazyOS-Desktop")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=DEFAULT_BG_COLOR)

        taskbar_hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        self.taskbar_manager = TaskbarManager(taskbar_hwnd, auto_hide=HIDE_WINDOWS_TASKBAR)
        self.taskbar_manager.hide()

        self.canvas = tk.Canvas(self.root, bg=DEFAULT_BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.window_manager = WindowManager(self.root, self.canvas)

        self._create_taskbar()

        self.theme_manager = ThemeManager(
            self.root,
            self.canvas,
            [self.start_button, self.clock_label],
            show_error_callback=lambda msg: self._show_messagebox("error", "Error", msg)
        )

        self._verify_system_files()
        self._create_desktop_icons()
        self._create_start_menu()
        self._create_context_menu()
        self._bind_events()
        self._update_clock()

        self.root.after(100, self._load_theme_on_startup)

        self._apply_system_settings()

        self._config_mtime = self._get_config_mtime()
        self.root.after(2000, self._poll_config)
        self.root.after(5000, self._check_target_date)

        if ConfigManager.bool_val(ConfigManager.load_config(), "system", "startup_sound", default=True):
            SoundManager.play('The Microsoft Sound.wav')
        logger.info("EazyOS Desktop initialized successfully")

    def _check_target_date(self) -> None:
        """Checks if the special event date has been reached"""
        current_time = datetime.datetime.now()
        if current_time >= target_date:
            self._run_special_event()
        self.root.after(3600000, self._check_target_date)

    def _run_special_event(self) -> None:
        """Action to run when the target date is reached"""
        
        self._show_messagebox(
            "warning",
            "EazyOS Out of Support Warning",
            "You are running a version of EazyOS that is no longer supported!"
        )

    def _get_config_mtime(self) -> float:
        try:
            return os.path.getmtime(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else 0.0
        except Exception:
            return 0.0

    def _poll_config(self) -> None:
        try:
            mtime = self._get_config_mtime()
            if mtime != self._config_mtime:
                self._config_mtime = mtime
                logger.info("Config file changed — reloading settings")
                self.theme_manager.apply_from_config()
                self._apply_system_settings()
        except Exception as e:
            logger.error(f"Config poll error: {e}")
        finally:
            self.root.after(2000, self._poll_config)

    def _apply_system_settings(self) -> None:
        config = ConfigManager.load_config()

        global ENABLE_SOUNDS
        ENABLE_SOUNDS = ConfigManager.bool_val(config, "system", "enable_sounds", default=True)

        show_clock = ConfigManager.bool_val(config, "system", "show_clock", default=True)
        try:
            if show_clock:
                self.canvas.itemconfigure(self.clock_window, state="normal")
            else:
                self.canvas.itemconfigure(self.clock_window, state="hidden")
        except Exception:
            pass

        auto_hide = ConfigManager.bool_val(config, "system", "auto_hide_windows_taskbar", default=True)
        self.taskbar_manager._auto_hide = auto_hide
        if auto_hide:
            self.taskbar_manager.hide()
        else:
            self.taskbar_manager.show()

        logger.info(f"System settings applied: sounds={ENABLE_SOUNDS}, clock={show_clock}, auto_hide_taskbar={auto_hide}")

    def _load_theme_on_startup(self):
        try:
            if DEBUG_THEME_LOADING:
                print("\n" + "="*60)
                print("DEBUG: Loading theme on startup...")
                print(f"Config file location: {CONFIG_FILE}")
                print(f"Config file exists: {os.path.exists(CONFIG_FILE)}")
                print("="*60 + "\n")
            self.theme_manager.load_saved_theme()
        except Exception as e:
            logger.error(f"Error loading theme on startup: {e}", exc_info=True)

    def _show_messagebox(self, msg_type: str, title: str, message: str) -> bool:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg="#C0C0C0")
        dialog.resizable(False, False)

        dialog_width = 380
        dialog_height = 140
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        content = tk.Frame(dialog, bg="#C0C0C0", relief="ridge", bd=4)
        content.pack(fill="both", expand=True)

        msg_frame = tk.Frame(content, bg="#C0C0C0")
        msg_frame.pack(fill="both", expand=True, padx=15, pady=15)

        icon_label = tk.Label(msg_frame, bg="#C0C0C0", font=("MS Sans Serif", 28))
        icon_label.pack(side="left", padx=(0, 15))

        if msg_type == "info":
            icon_label.config(text="ℹ", fg="#0000FF")
        elif msg_type == "warning":
            icon_label.config(text="⚠", fg="#FF8C00")
        elif msg_type == "error":
            icon_label.config(text="✖", fg="#FF0000")
        elif msg_type in ["askyesno", "askokcancel"]:
            icon_label.config(text="?", fg="#0000FF", font=("MS Sans Serif", 28, "bold"))

        msg_label = tk.Label(msg_frame, text=message, bg="#C0C0C0", fg="black",
                             font=("MS Sans Serif", 9), justify="left",
                             wraplength=250, anchor="w")
        msg_label.pack(side="left", fill="both", expand=True)

        btn_frame = tk.Frame(content, bg="#C0C0C0")
        btn_frame.pack(side="bottom", pady=(5, 15))

        result = {"value": False}

        def close_dialog(value=False):
            result["value"] = value
            try:
                dialog.grab_release()
            except:
                pass
            try:
                dialog.destroy()
            except:
                pass

        def create_win98_button(parent, text, command):
            return tk.Button(parent, text=text, width=10, height=1,
                             bg="#C0C0C0", fg="black", font=("MS Sans Serif", 8, "bold"),
                             relief="raised", bd=2, activebackground="#DFDFDF",
                             activeforeground="black", command=command, cursor="hand2")

        if msg_type in ["info", "warning", "error"]:
            ok_btn = create_win98_button(btn_frame, "OK", lambda: close_dialog(True))
            ok_btn.pack(padx=5)
            dialog.bind("<Return>", lambda e: close_dialog(True))
            dialog.bind("<Escape>", lambda e: close_dialog(True))
            dialog.after(100, lambda: ok_btn.focus_set())

        elif msg_type == "askyesno":
            yes_btn = create_win98_button(btn_frame, "Yes", lambda: close_dialog(True))
            yes_btn.pack(side="left", padx=5)
            no_btn = create_win98_button(btn_frame, "No", lambda: close_dialog(False))
            no_btn.pack(side="left", padx=5)
            dialog.bind("<Return>", lambda e: close_dialog(True))
            dialog.bind("<Escape>", lambda e: close_dialog(False))
            dialog.after(100, lambda: yes_btn.focus_set())

        elif msg_type == "askokcancel":
            ok_btn = create_win98_button(btn_frame, "OK", lambda: close_dialog(True))
            ok_btn.pack(side="left", padx=5)
            cancel_btn = create_win98_button(btn_frame, "Cancel", lambda: close_dialog(False))
            cancel_btn.pack(side="left", padx=5)
            dialog.bind("<Return>", lambda e: close_dialog(True))
            dialog.bind("<Escape>", lambda e: close_dialog(False))
            dialog.after(100, lambda: ok_btn.focus_set())

        if ENABLE_SOUNDS:
            try:
                if msg_type in ["error", "warning"]:
                    for sound_name in ['CHORD.wav', 'chord.wav']:
                        if os.path.exists(os.path.join(MEDIA_DIR, sound_name)):
                            SoundManager.play(sound_name, async_play=False)
                            break
                else:
                    for sound_name in ['DING.wav', 'ding.wav']:
                        if os.path.exists(os.path.join(MEDIA_DIR, sound_name)):
                            SoundManager.play(sound_name, async_play=False)
                            break
            except Exception as e:
                logger.warning(f"Failed to play messagebox sound: {e}")

        dialog.transient(self.root)
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        dialog.update_idletasks()

        try:
            dialog.wait_window(dialog)
        except:
            pass

        return result["value"]

    def _create_taskbar(self) -> None:
        self.start_button = tk.Button(self.root, text="Start", bg=TASKBAR_COLOR,
                                      fg="black", relief="raised",
                                      font=("MS Sans Serif", 9, "bold"), padx=10, pady=2)
        self.button_window = self.canvas.create_window(10, 0, anchor="w", window=self.start_button)

        self.clock_label = tk.Label(self.root, font=("MS Sans Serif", 9), bg=TASKBAR_COLOR,
                                    fg="black", relief="sunken", bd=1, padx=5, pady=2)
        self.clock_window = self.canvas.create_window(0, 0, anchor="e", window=self.clock_label)

    def _draw_taskbar(self, event=None) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return

        self.canvas.delete("taskbar")
        y1 = h - TASKBAR_HEIGHT
        y2 = h

        self.canvas.create_rectangle(0, y1, w, y2, fill=TASKBAR_COLOR, outline="", tags="taskbar")
        self.canvas.create_line(0, y1, w, y1, fill=TASKBAR_LIGHT, width=2, tags="taskbar")
        self.canvas.create_line(0, y2 - 1, w, y2 - 1, fill=TASKBAR_DARK, width=1, tags="taskbar")

        self.canvas.coords(self.button_window, 10, y1 + TASKBAR_HEIGHT // 2)
        self.canvas.coords(self.clock_window, w - 10, y1 + TASKBAR_HEIGHT // 2)
        self.canvas.tag_raise(self.button_window)
        self.canvas.tag_raise(self.clock_window)
        self.canvas.tag_raise("taskbar_button")

    def _update_clock(self) -> None:
        if self.root.winfo_exists():
            self.clock_label.config(text=time.strftime("%I:%M %p"))
            self.root.after(1000, self._update_clock)

    def _verify_system_files(self) -> None:
        required_files = [
            ('bios.py', 'BIOS system file'),
            ('bsod.py', 'BSOD system file'),
            ('SYSTEM', 'System directory')
        ]
        for filename, description in required_files:
            if not os.path.exists(filename):
                logger.warning(f"{description} not found: {filename}")

    def _create_desktop_icons(self) -> None:
        icon_y = 20
        icon_x = 20
        icon_configs = [
            ("notepad.png", self._open_notepad, "Notepad"),
            ("group.png", self._open_games, "Games"),
            ("player.png", self._open_music, "Music"),
            ("internet.png", self._open_internet, "Internet"),
            ("control.png", self._open_control, "Contol Panel"),
            ("explorer.png", self._open_file_explorer, "Explorer"),
            ("calc.png", self._open_calculator, "Calculator"),
            ("paint.png", self._open_paint, "Paint"),
            ("clock.png", self._open_alarm, "Alarm"),
            ("internetshortcut.png", self._open_contact, "Contact Me!"),
            
            
        ]
        for icon_file, command, label in icon_configs:
            offset = self._add_desktop_icon(icon_file, command, label, icon_x, icon_y)
            icon_y += offset

    def _add_desktop_icon(self, icon_file: str, command: Callable,
                          label: str, x: int, y: int) -> int:
        try:
            icon_path = os.path.join(ICONS_DIR, icon_file)
            if not os.path.exists(icon_path):
                logger.warning(f"Icon not found: {icon_path}")
                return 40

            img = tk.PhotoImage(file=icon_path)
            btn = tk.Button(self.root, image=img, command=command, bd=0,
                            bg=DEFAULT_BG_COLOR, activebackground=DEFAULT_BG_COLOR, relief="flat")
            btn.image = img
            self.canvas.create_window(x, y, anchor="nw", window=btn)

            lbl = tk.Label(self.root, text=label, bg=DEFAULT_BG_COLOR,
                           fg=DESKTOP_FG_COLOR, font=("MS Sans Serif", 8))
            label_y = y + img.height() + 2
            self.canvas.create_window(x + img.width() // 2, label_y, anchor="n", window=lbl)

            return img.height() + 20
        except Exception as e:
            logger.error(f"Failed to create icon {label}: {e}")
            return 40

    def _create_start_menu(self) -> None:
        self.start_menu = tk.Menu(self.root, tearoff=0, bg="white", fg="black",
                                  activebackground=WIN98_BLUE, activeforeground="white")

        self.start_menu.add_command(label="EazyOS 3", state="disabled")
        self.start_menu.add_separator()
        self.start_menu.add_command(label="About EazyOS", command=self._open_about)
        self.start_menu.add_command(label="Update EazyOS", command=self._open_update)
        self.start_menu.add_separator()

        programs_menu = self._create_programs_menu()
        self.start_menu.add_cascade(label="Programs", menu=programs_menu)

        self.start_menu.add_separator()

        self.start_menu.add_command(label="Control Panel", command=self._open_control)

        self.start_menu.add_command(label="Change Username and Password", command=self._manage_users)

        screensaver_menu = tk.Menu(self.start_menu, tearoff=0, bg="white", fg="black",
                                   activebackground=WIN98_BLUE, activeforeground="white")
        screensaver_menu.add_command(label="Bubbles", command=self._open_screensaver_bubbles)
        screensaver_menu.add_command(label="DVD", command=self._open_screensaver_dvd)
        self.start_menu.add_cascade(label="Screensaver", menu=screensaver_menu)

        self.start_menu.add_separator()
        self.start_menu.add_command(label="Restart", command=self._restart)
        self.start_menu.add_command(label="Logout", command=self._logout)
        self.start_menu.add_command(label="Shutdown", command=self._exit)

        self.start_button.config(command=self._show_start_menu)

    def _create_sys_program(self) -> tk.Menu:
        sys_program = tk.Menu(self.start_menu, tearoff=0, bg="white", fg="black",
                              activebackground=WIN98_BLUE, activeforeground="white")
        sys_program.add_command(label="Task Manager", command=self._open_task_manager)
        sys_program.add_command(label="DOS Prompt", command=self._open_dos_prompt)
        sys_program.add_command(label="Regedit", command=self._open_regedit)
        return sys_program

    def _create_programs_menu(self) -> tk.Menu:
        programs = tk.Menu(self.start_menu, tearoff=0, bg="white", fg="black",
                           activebackground=WIN98_BLUE, activeforeground="white")
        programs.add_command(label="Notepad", command=self._open_notepad)
        programs.add_command(label="Games", command=self._open_games)
        programs.add_command(label="Music Player", command=self._open_music)
        programs.add_command(label="Internet Explorer", command=self._open_internet)
        programs.add_command(label="File Explorer", command=self._open_file_explorer)
        programs.add_command(label="Paint", command=self._open_paint)
        programs.add_command(label="Calculator", command=self._open_calculator)
        programs.add_command(label="Alarm", command=self._open_alarm)
        programs.add_separator()

        sys_program = self._create_sys_program()
        programs.add_cascade(label="System Programs", menu=sys_program)

        return programs

    def _create_context_menu(self) -> None:
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="white", fg="black",
                                    activebackground=WIN98_BLUE, activeforeground="white")
        self.context_menu.add_command(label="EazyOS 3", state="disabled")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Notepad", command=self._open_notepad)
        self.context_menu.add_command(label="Games", command=self._open_games)
        self.context_menu.add_command(label="Internet Explorer", command=self._open_internet)
        self.context_menu.add_command(label="File Explorer", command=self._open_file_explorer)
        self.context_menu.add_command(label="Calculator", command=self._open_calculator)
        self.context_menu.add_command(label="Paint", command=self._open_paint)
     
        self.context_menu.add_command(label="Control Panel", command=self._open_control)

    def _bind_events(self) -> None:
        self.root.bind("<Configure>", self._draw_taskbar)
        self.root.bind("<Escape>", lambda e: self._exit())
        self.root.bind("<Button-3>", self._show_context_menu)
        self.root.bind("<Control-Shift-B>", lambda e: self._trigger_bsod())
        self.root.bind("<Key>", self._on_key)
        self._draw_taskbar()

    def _show_start_menu(self) -> None:
        try:
            y_pos = self.root.winfo_height() - TASKBAR_HEIGHT - 5
            self.start_menu.tk_popup(5, y_pos)
        finally:
            self.start_menu.grab_release()

    def _show_context_menu(self, event) -> None:
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _on_key(self, event) -> None:
        ctrl = event.state & 0x4
        alt = event.state & 0x20000
        if ctrl and alt and event.keysym.lower() == "backspace":
            self._open_task_manager()

    # === PROGRAM LAUNCHERS ===

    def _open_notepad(self):
        script = os.path.join(PROGRAM_FILES_DIR, "notepad", "notepad.py")
        self.window_manager.create_window("Notepad", script)

    def _open_calculator(self):
        script = os.path.join(PROGRAM_FILES_DIR, "calc", "calc.py")
        self.window_manager.create_window("Calculator", script)

    def _open_paint(self):
        script = os.path.join(PROGRAM_FILES_DIR, "paint", "main.py")
        self.window_manager.create_window("Paint", script)

    def _open_games(self):
        script = os.path.join(PROGRAM_FILES_DIR, "Games", "select.py")
        self.window_manager.create_window("Games", script)

    def _open_music(self):
        script = os.path.join(PROGRAM_FILES_DIR, "Sound Player", "music_player.py")
        self.window_manager.create_window("Music Player", script)

    def _open_internet(self):
        script = os.path.join(BASE_DIR, "internet explorer", "select.py")
        self.window_manager.create_window("Internet Explorer", script)
    def _open_contact(self):
        script = os.path.join(BASE_DIR, "internet explorer", "contact.py")
        self.window_manager.create_window("Contact Me!", script)
        
    

    def _open_file_explorer(self):
        script = os.path.join(PROGRAM_FILES_DIR, "file", "src", "main.py")
        self.window_manager.create_window("File Explorer", script)

    def _open_dos_prompt(self):
        script = os.startfile("SYSTEM\CMD.py")	
        self.window_manager.create_window("DOS Prompt", script)

    def _open_alarm(self):
        script = os.path.join(PROGRAM_FILES_DIR, "alarm", "alarm.py")
        self.window_manager.create_window("Alarm", script)

    def _open_task_manager(self):
        script = os.path.join(SYSTEM_DIR, "taskmgr.py")
        self.window_manager.create_window("Task Manager", script)

    def _open_regedit(self):
        script = os.path.join(SYSTEM_DIR, "regedit.py")
        self.window_manager.create_window("Regedit", script)

    def _open_about(self):
        script = os.path.join(SYSTEM_DIR, "about.py")
        self.window_manager.create_window("About EazyOS", script, width=400, height=300)

    def _open_update(self):
        SoundManager.play('DING.wav')
        if self._show_messagebox("askyesno", "Update", "Are you sure you want to upgrade?"):
            script = os.startfile(r"setup\UPDATEOS.py")
            self.window_manager.create_window("Update", script)

    def _open_screensaver_bubbles(self):
        script = os.path.join(PROGRAM_FILES_DIR, "screensaver", "bubbles.py")
        self.window_manager.create_window("Bubbles Screensaver", script)

    def _open_screensaver_dvd(self):
        script = os.path.join(PROGRAM_FILES_DIR, "screensaver", "main.py")
        self.window_manager.create_window("DVD Screensaver", script)
    def _open_control(self):
        script = os.path.join(BASE_DIR,"control.py")
        self.window_manager.create_window("Control Panel", script)

    def _trigger_bsod(self):
        script = os.path.join(BASE_DIR, "BSOD.py")
        self.window_manager.create_window("BSOD", script)
        self.root.after(500, self._exit)

    def _manage_users(self):
        bat_path = os.path.join(SYSTEM_DIR, "User.bat")  # your batch file
        self._run_bat_terminal(bat_path)

    def _run_bat_terminal(self, bat_path: str):
        try:
            # Open in a new CMD window
            subprocess.Popen(
                f'start cmd /k "{bat_path}"',
                shell=True
            )
        except Exception as e:
            print(f"Failed to open CMD: {e}")

   
    # === SYSTEM COMMANDS ===
    def _restart(self):
        SoundManager.play('DING.wav')
        if self._show_messagebox("askokcancel", "Restart?", "Are you sure you want to restart?"):
            SoundManager.play('shutdown.wav')
            time.sleep(4)
            self.taskbar_manager.show()
            self.root.destroy()
            subprocess.run([sys.executable, os.path.join(SYSTEM_DIR, "restartdialog.py")])

    def _logout(self):
        SoundManager.play('DING.wav')
        if self._show_messagebox("askokcancel", "Logout?", "Are you sure you want to log out?"):
            self.taskbar_manager.show()
            self.root.destroy()
            subprocess.run([sys.executable, os.path.join(SYSTEM_DIR, "logoutdialog.py")])
           

    def _exit(self):
        SoundManager.play('DING.wav')
        if self._show_messagebox("askokcancel", "Shutdown?", "Are you sure you want to Shutdown?"):
            SoundManager.play('shutdown.wav')
            time.sleep(4)
            self.taskbar_manager.show()
            self.root.destroy()
            subprocess.run([sys.executable, os.path.join(SYSTEM_DIR, "shtdowndialog.py")])

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Desktop interrupted by user")
            self._exit()
        finally:
            self.taskbar_manager.show()


# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    try:
        desktop = EazyOSDesktop()
        desktop.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        messagebox.showerror("EazyOS Fatal Error", f"EazyOS has encountered a critical error:\n{e}")
        sys.exit(1)
