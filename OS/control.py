import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import json
import os
import sys
import subprocess
import logging

# === CONSTANTS (match EazyOS) ===
WIN98_BLUE      = "#000080"
WIN98_GRAY      = "#C0C0C0"
WIN98_DARK      = "#808080"
WIN98_WHITE     = "#FFFFFF"
WIN98_BLACK     = "#000000"
WIN98_LIGHT     = "#DFDFDF"

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE   = os.path.join(BASE_DIR, "eazyos_config.json")
MEDIA_DIR     = os.path.join(BASE_DIR, "media")
WALLPAPER_DIR = os.path.join(MEDIA_DIR, "wallpaper")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === DEFAULT CONFIG ===
DEFAULT_CONFIG = {
    "theme": {
        "type": "color",
        "color": "#008080",
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

# ─── Helpers ────────────────────────────────────────────────────────────────

def load_config():
    import copy
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            for section, defaults in cfg.items():
                if section not in data:
                    data[section] = defaults
                elif isinstance(defaults, dict):
                    for k, v in defaults.items():
                        data[section].setdefault(k, v)
            return data
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
    return cfg


def save_config(cfg):
    try:
        # Load whatever is currently on disk
        existing = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                existing = json.load(f)

        # Deep merge: only overwrite keys we have, preserve everything else
        for section, values in cfg.items():
            if section not in existing:
                existing[section] = values
            elif isinstance(values, dict):
                for k, v in values.items():
                    existing[section][k] = v
            else:
                existing[section] = values

        with open(CONFIG_FILE, "w") as f:
            json.dump(existing, f, indent=4)

        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


def bool_str(val):
    return "true" if val else "false"


# ─── Win98 Widget Helpers ────────────────────────────────────────────────────

def win98_button(parent, text, command, width=12):
    return tk.Button(
        parent, text=text, command=command,
        bg=WIN98_GRAY, fg=WIN98_BLACK,
        font=("MS Sans Serif", 8), relief="raised", bd=2,
        activebackground=WIN98_LIGHT, activeforeground=WIN98_BLACK,
        width=width, cursor="hand2"
    )


def win98_label(parent, text, bold=False, fg=WIN98_BLACK):
    font = ("MS Sans Serif", 8, "bold") if bold else ("MS Sans Serif", 8)
    return tk.Label(parent, text=text, bg=WIN98_GRAY, fg=fg, font=font)


def win98_check(parent, text, var):
    return tk.Checkbutton(
        parent, text=text, variable=var,
        bg=WIN98_GRAY, fg=WIN98_BLACK,
        font=("MS Sans Serif", 8),
        activebackground=WIN98_GRAY,
        selectcolor=WIN98_WHITE,
        relief="flat"
    )


def separator(parent):
    tk.Frame(parent, bg=WIN98_DARK, height=1).pack(fill="x", padx=6, pady=4)


def section_box(parent, title):
    outer = tk.LabelFrame(
        parent, text=title,
        bg=WIN98_GRAY, fg=WIN98_BLACK,
        font=("MS Sans Serif", 8, "bold"),
        relief="groove", bd=2,
        padx=8, pady=6
    )
    outer.pack(fill="x", padx=10, pady=6)
    return outer


# ─── Title Bar ───────────────────────────────────────────────────────────────

def make_title_bar(win, title, on_close):
    bar = tk.Frame(win, bg=WIN98_BLUE, height=22)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    tk.Label(
        bar, text=title, bg=WIN98_BLUE, fg="white",
        font=("MS Sans Serif", 9, "bold")
    ).pack(side="left", padx=6, pady=2)

    tk.Button(
        bar, text="✕", width=3, bg=WIN98_GRAY,
        font=("MS Sans Serif", 8, "bold"), relief="raised", bd=1,
        command=on_close
    ).pack(side="right", padx=2, pady=2)

    def start(e):
        bar._x, bar._y = e.x, e.y

    def drag(e):
        dx = e.x - bar._x
        dy = e.y - bar._y
        win.geometry(f"+{win.winfo_x() + dx}+{win.winfo_y() + dy}")

    bar.bind("<ButtonPress-1>", start)
    bar.bind("<B1-Motion>", drag)


# ─── Panel Pages ─────────────────────────────────────────────────────────────

class DisplayPage(tk.Frame):
    def __init__(self, parent, cfg, on_save):
        super().__init__(parent, bg=WIN98_GRAY)
        self.cfg = cfg
        self.on_save = on_save
        self._build()

    def _build(self):
        win98_label(self, "Display Settings", bold=True).pack(anchor="w", padx=10, pady=(10, 2))
        separator(self)

        # --- Desktop background color ---
        box = section_box(self, "Desktop Background")
        self._color_preview = tk.Label(
            box, width=6, height=2,
            bg=self.cfg["theme"].get("color") or "#008080",
            relief="sunken", bd=2
        )
        self._color_preview.grid(row=0, column=0, padx=(0, 8))
        win98_label(box, "Background Color:").grid(row=0, column=1, sticky="w")
        win98_button(box, "Choose...", self._pick_color, width=10).grid(row=0, column=2, padx=6)

        # --- Wallpaper ---
        box2 = section_box(self, "Wallpaper")

        win98_label(box2, "Default Backgrounds:").pack(anchor="w", pady=(0, 4))

        list_frame = tk.Frame(box2, bg=WIN98_GRAY)
        list_frame.pack(fill="x")

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self._wp_list = tk.Listbox(
            list_frame, height=5, yscrollcommand=scrollbar.set,
            bg=WIN98_WHITE, fg=WIN98_BLACK,
            font=("MS Sans Serif", 8),
            selectbackground=WIN98_BLUE, selectforeground="white",
            relief="sunken", bd=2, activestyle="none"
        )
        scrollbar.config(command=self._wp_list.yview)
        self._wp_list.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="left", fill="y")

        # Populate list from media/wallpaper/
        self._wp_paths = {}
        os.makedirs(WALLPAPER_DIR, exist_ok=True)
        for f in sorted(os.listdir(WALLPAPER_DIR)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                self._wp_list.insert("end", f)
                self._wp_paths[f] = os.path.join(WALLPAPER_DIR, f)

        # Pre-select active wallpaper
        current_wp = self.cfg["theme"].get("wallpaper")
        if current_wp:
            current_name = os.path.basename(current_wp)
            for i, name in enumerate(self._wp_paths):
                if name == current_name:
                    self._wp_list.selection_set(i)
                    self._wp_list.see(i)
                    break

        # Current wallpaper label — sunken field above buttons
        self._wp_label = tk.Label(
            box2,
            text=self._short_path(self.cfg["theme"].get("wallpaper")),
            bg=WIN98_WHITE, fg=WIN98_BLACK,
            font=("MS Sans Serif", 8), relief="sunken", bd=1,
            anchor="w", padx=4
        )
        self._wp_label.pack(fill="x", pady=(6, 4))

        btn_row = tk.Frame(box2, bg=WIN98_GRAY)
        btn_row.pack(fill="x", pady=(2, 0))
        win98_button(btn_row, "Set Wallpaper", self._set_from_list, width=14).pack(side="left", padx=(0, 6))
        win98_button(btn_row, "Browse...", self._pick_wallpaper, width=10).pack(side="left")
        win98_button(btn_row, "Clear", self._clear_wallpaper, width=8).pack(side="left", padx=6)

        # --- Taskbar color ---
        box3 = section_box(self, "Taskbar")
        self._tb_preview = tk.Label(
            box3, width=6, height=2,
            bg=self.cfg["theme"].get("taskbar_color", "#c0c0c0"),
            relief="sunken", bd=2
        )
        self._tb_preview.grid(row=0, column=0, padx=(0, 8))
        win98_label(box3, "Taskbar Color:").grid(row=0, column=1, sticky="w")
        win98_button(box3, "Choose...", self._pick_taskbar, width=10).grid(row=0, column=2, padx=6)

        # --- Window title bar color ---
        box4 = section_box(self, "Window Title Bar")
        self._title_preview = tk.Label(
            box4, width=6, height=2,
            bg=self.cfg["theme"].get("window_title_color", WIN98_BLUE),
            relief="sunken", bd=2
        )
        self._title_preview.grid(row=0, column=0, padx=(0, 8))
        win98_label(box4, "Title Bar Color:").grid(row=0, column=1, sticky="w")
        win98_button(box4, "Choose...", self._pick_titlebar, width=10).grid(row=0, column=2, padx=6)

        separator(self)
        btn_row2 = tk.Frame(self, bg=WIN98_GRAY)
        btn_row2.pack(padx=10, pady=4, anchor="w")
        win98_button(btn_row2, "Reset Default", self._reset, width=14).pack(side="left", padx=(0, 6))
        win98_button(btn_row2, "Apply", self._apply, width=10).pack(side="left")

    def _short_path(self, path):
        if not path:
            return "Current wallpaper: (none)"
        return f"Current wallpaper: {os.path.basename(path)}"

    def _set_from_list(self):
        sel = self._wp_list.curselection()
        if not sel:
            return
        name = self._wp_list.get(sel[0])
        path = self._wp_paths.get(name)
        if path and os.path.exists(path):
            self.cfg["theme"]["wallpaper"] = path
            self.cfg["theme"]["type"] = "wallpaper"
            self._wp_label.config(text=self._short_path(path))

    def _pick_wallpaper(self):
        path = filedialog.askopenfilename(
            title="Select Wallpaper",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if path:
            self.cfg["theme"]["wallpaper"] = path
            self.cfg["theme"]["type"] = "wallpaper"
            self._wp_label.config(text=self._short_path(path))
            name = os.path.basename(path)
            if name not in self._wp_paths:
                self._wp_list.insert("end", name)
                self._wp_paths[name] = path
            items = list(self._wp_paths.keys())
            if name in items:
                idx = items.index(name)
                self._wp_list.selection_clear(0, "end")
                self._wp_list.selection_set(idx)
                self._wp_list.see(idx)

    def _clear_wallpaper(self):
        self.cfg["theme"]["wallpaper"] = None
        self.cfg["theme"]["type"] = "color"
        self._wp_list.selection_clear(0, "end")
        self._wp_label.config(text=self._short_path(None))

    def _pick_color(self):
        c = colorchooser.askcolor(
            title="Choose Background Color",
            initialcolor=self.cfg["theme"].get("color") or "#008080"
        )
        if c and c[1]:
            self.cfg["theme"]["color"] = c[1]
            self.cfg["theme"]["type"] = "color"
            self.cfg["theme"]["wallpaper"] = None
            self._color_preview.config(bg=c[1])
            self._wp_label.config(text=self._short_path(None))
            self._wp_list.selection_clear(0, "end")

    def _pick_taskbar(self):
        c = colorchooser.askcolor(
            title="Choose Taskbar Color",
            initialcolor=self.cfg["theme"].get("taskbar_color", "#c0c0c0")
        )
        if c and c[1]:
            self.cfg["theme"]["taskbar_color"] = c[1]
            self._tb_preview.config(bg=c[1])

    def _pick_titlebar(self):
        c = colorchooser.askcolor(
            title="Choose Title Bar Color",
            initialcolor=self.cfg["theme"].get("window_title_color", WIN98_BLUE)
        )
        if c and c[1]:
            self.cfg["theme"]["window_title_color"] = c[1]
            self._title_preview.config(bg=c[1])

    def _reset(self):
        self.cfg["theme"] = {
            "type": "color",
            "color": "#008080",
            "wallpaper": None,
            "taskbar_color": "#c0c0c0",
            "window_title_color": WIN98_BLUE
        }
        self._color_preview.config(bg="#008080")
        self._tb_preview.config(bg="#c0c0c0")
        self._title_preview.config(bg=WIN98_BLUE)
        self._wp_label.config(text=self._short_path(None))
        self._wp_list.selection_clear(0, "end")
        self._apply()

    def _apply(self):
        self.on_save(self.cfg)


class SoundPage(tk.Frame):
    def __init__(self, parent, cfg, on_save):
        super().__init__(parent, bg=WIN98_GRAY)
        self.cfg = cfg
        self.on_save = on_save
        self._build()

    def _build(self):
        win98_label(self, "Sound Settings", bold=True).pack(anchor="w", padx=10, pady=(10, 2))
        separator(self)

        box = section_box(self, "Sound Events")
        self._startup = tk.BooleanVar(value=self.cfg["system"].get("startup_sound", "true") == "true")
        self._sounds  = tk.BooleanVar(value=self.cfg["system"].get("enable_sounds",  "true") == "true")

        win98_check(box, "Play startup sound", self._startup).pack(anchor="w", pady=2)
        win98_check(box, "Enable all system sounds", self._sounds).pack(anchor="w", pady=2)

        separator(self)
        win98_button(self, "Apply", self._apply, width=10).pack(padx=10, pady=4, anchor="w")

    def _apply(self):
        self.cfg["system"]["startup_sound"] = bool_str(self._startup.get())
        self.cfg["system"]["enable_sounds"]  = bool_str(self._sounds.get())
        self.on_save(self.cfg)


class SystemPage(tk.Frame):
    def __init__(self, parent, cfg, on_save):
        super().__init__(parent, bg=WIN98_GRAY)
        self.cfg = cfg
        self.on_save = on_save
        self._build()

    def _build(self):
        win98_label(self, "System Settings", bold=True).pack(anchor="w", padx=10, pady=(10, 2))
        separator(self)

        box = section_box(self, "Taskbar & Clock")
        self._clock    = tk.BooleanVar(value=self.cfg["system"].get("show_clock", "true") == "true")
        self._autohide = tk.BooleanVar(value=self.cfg["system"].get("auto_hide_windows_taskbar", "true") == "true")

        win98_check(box, "Show clock in taskbar", self._clock).pack(anchor="w", pady=2)
        win98_check(box, "Auto-hide Windows taskbar", self._autohide).pack(anchor="w", pady=2)

        box2 = section_box(self, "System Information")
        info = [
            ("OS Name",     "EazyOS 3"),
            ("Version",     "3.0"),
            ("Build",       "Desktop Shell"),
            ("Config File", os.path.basename(CONFIG_FILE)),
        ]
        for i, (k, v) in enumerate(info):
            win98_label(box2, f"{k}:").grid(row=i, column=0, sticky="w", pady=1)
            win98_label(box2, v, fg=WIN98_BLUE).grid(row=i, column=1, sticky="w", padx=12, pady=1)

        separator(self)
        win98_button(self, "Apply", self._apply, width=10).pack(padx=10, pady=4, anchor="w")

    def _apply(self):
        self.cfg["system"]["show_clock"]                = bool_str(self._clock.get())
        self.cfg["system"]["auto_hide_windows_taskbar"] = bool_str(self._autohide.get())
        self.on_save(self.cfg)


class AboutPage(tk.Frame):
    def __init__(self, parent, cfg, on_save):
        super().__init__(parent, bg=WIN98_GRAY)
        self._build()

    def _build(self):
        win98_label(self, "About EazyOS", bold=True).pack(anchor="w", padx=10, pady=(10, 2))
        separator(self)

        box = section_box(self, "EazyOS Control Panel")
        lines = [
            ("EazyOS Control Panel",                     True),
            ("",                                          False),
            ("Version 3.0",                               False),
            ("A Windows 98-style desktop environment.",   False),
            ("",                                          False),
            ("Settings are saved to eazyos_config.json", False),
            ("Changes take effect automatically.",         False),
        ]
        for text, bold in lines:
            win98_label(box, text, bold=bold).pack(anchor="w", pady=1)


# ─── Main Control Panel Window ───────────────────────────────────────────────

PANEL_ITEMS = [
    ("  Display",  "display", DisplayPage),
    ("  Sound",    "sound",   SoundPage),
    ("  System",   "system",  SystemPage),
    ("  About",    "about",   AboutPage),
]


class ControlPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EazyOS Control Panel")
        self.root.resizable(False, False)
        self.root.minsize(580, 560)
        self.root.configure(bg=WIN98_GRAY)
        self.root.overrideredirect(True)

        self.cfg = load_config()
        self._build()
        self._center()

    def _center(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build(self):
        # Custom Win98 title bar (draggable)
        make_title_bar(self.root, "Control Panel", self._close)

        # Menu bar strip
        menu_bar = tk.Frame(self.root, bg=WIN98_GRAY, relief="flat")
        menu_bar.pack(fill="x")
        for label in ("File", "View", "Help"):
            tk.Label(
                menu_bar, text=label, bg=WIN98_GRAY, fg=WIN98_BLACK,
                font=("MS Sans Serif", 8), padx=6, pady=2, cursor="hand2"
            ).pack(side="left")

        tk.Frame(self.root, bg=WIN98_DARK, height=1).pack(fill="x")

        # Body
        body = tk.Frame(self.root, bg=WIN98_GRAY)
        body.pack(fill="both", expand=True)

        # Left sidebar
        list_frame = tk.Frame(body, bg=WIN98_WHITE, width=140,
                               relief="sunken", bd=2)
        list_frame.pack(side="left", fill="y", padx=(8, 0), pady=8)
        list_frame.pack_propagate(False)

        self._buttons = {}
        self._pages   = {}

        # Right content pane
        self._content = tk.Frame(body, bg=WIN98_GRAY, width=420, height=520,
                                  relief="sunken", bd=2)
        self._content.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self._content.pack_propagate(False)

        # Build sidebar buttons and pages
        for label, key, PageClass in PANEL_ITEMS:
            btn = tk.Button(
                list_frame, text=label, anchor="w",
                bg=WIN98_WHITE, fg=WIN98_BLACK,
                font=("MS Sans Serif", 9), relief="flat",
                activebackground=WIN98_BLUE, activeforeground="white",
                padx=6, pady=4, width=14,
                command=lambda k=key: self._show(k)
            )
            btn.pack(fill="x", pady=1)
            self._buttons[key] = btn

            page = PageClass(self._content, self.cfg, self._on_save)
            self._pages[key] = page

        # Status bar + close button
        tk.Frame(self.root, bg=WIN98_DARK, height=1).pack(fill="x")
        btn_row = tk.Frame(self.root, bg=WIN98_GRAY)
        btn_row.pack(fill="x", padx=8, pady=6)

        self._status = tk.Label(
            btn_row, text="Select a category on the left.",
            bg=WIN98_GRAY, fg=WIN98_DARK,
            font=("MS Sans Serif", 8), anchor="w"
        )
        self._status.pack(side="left", fill="x", expand=True)

        win98_button(btn_row, "Close", self._close, width=8).pack(side="right", padx=(4, 0))

        # Show default page
        self._show("display")

    def _show(self, key):
        for k, btn in self._buttons.items():
            btn.config(bg=WIN98_WHITE, fg=WIN98_BLACK, relief="flat")
        self._buttons[key].config(bg=WIN98_BLUE, fg="white", relief="flat")

        for page in self._pages.values():
            page.place_forget()
        self._pages[key].place(x=0, y=0, relwidth=1, relheight=1)

    def _on_save(self, cfg):
        self.cfg = cfg
        if save_config(cfg):
            self._status.config(text="✔ Settings saved successfully.", fg="#006600")
            self.root.after(3000, lambda: self._status.config(
                text="Select a category on the left.", fg=WIN98_DARK))
        else:
            self._status.config(text="✖ Failed to save settings.", fg="#cc0000")

    def _close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = ControlPanel()
        app.run()
    except Exception as e:
        logging.exception("Control Panel error")
        messagebox.showerror("Control Panel Error", str(e))
        sys.exit(1)