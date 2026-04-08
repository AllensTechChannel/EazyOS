import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import sys
import time

root = tk.Tk()
root.title("EazyOS-Booting")
root.configure(bg="black")

# Play boot sound
try:
    import winsound
    winsound.PlaySound('media/startup-beep.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
    time.sleep(1)
    winsound.PlaySound('media/bootsound.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
except Exception:
    pass

# === Fullscreen ===
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())

# ── Win98 colours ──────────────────────────────────────────────
WIN98_TEAL   = "#008080"   # classic desktop teal
WIN98_GRAY   = "#C0C0C0"   # window chrome grey
WIN98_DARK   = "#000080"   # title-bar navy
WIN98_BLACK  = "#000000"
WIN98_WHITE  = "#FFFFFF"
WIN98_YELLOW = "#FFFF00"   # boot-progress yellow

# ── Fonts ──────────────────────────────────────────────────────
FONT_TITLE   = ("Fixedsys",  20, "bold")
FONT_BODY    = ("Courier New", 13)
FONT_SMALL   = ("Courier New", 10)
FONT_SPINNER = ("Courier New", 18, "bold")

# ──────────────────────────────────────────────────────────────
# ROOT  – plain black background (like a real POST screen)
root.configure(bg=WIN98_BLACK)

# ── TOP BIOS-style header bar ──────────────────────────────────
header = tk.Frame(root, bg=WIN98_DARK, pady=4)
header.pack(fill="x", side="top")

tk.Label(header, text="EazyOS  v1.0.1  BIOS  (C) 1998-2026",
         bg=WIN98_DARK, fg=WIN98_WHITE,
         font=FONT_BODY).pack(side="left", padx=10)

tk.Label(header, text="Press F8 to Enter Setup",
         bg=WIN98_DARK, fg=WIN98_YELLOW,
         font=FONT_BODY).pack(side="right", padx=10)

tk.Label(header, text="Press F6 to Enter Safe Mode",
         bg=WIN98_DARK, fg=WIN98_YELLOW,
         font=FONT_BODY).pack(side="right", padx=10)

# ── SCANLINE CANVAS (gives a CRT feel) ────────────────────────
# We draw faint horizontal grey lines over the whole window
def draw_scanlines(canvas, w, h):
    for y in range(0, h, 4):
        canvas.create_line(0, y, w, y, fill="#111111", width=1)

# ── MAIN CONTENT AREA ─────────────────────────────────────────
main_frame = tk.Frame(root, bg=WIN98_BLACK)
main_frame.pack(expand=True)

# RAM / CPU spoof lines (Win98 POST style)
post_lines = [
    "Award Modular BIOS v4.51PG, An Energy Star Ally",
    "Copyright (C) 1984-99, Award Software, Inc.",
    "",
    "EazyOS  i486DX2-66  Processor  64MB RAM",
    "Detecting Primary Master  ... EazyOS HDD  8192MB",
    "Detecting Primary Slave   ... None",
    "Detecting Secondary Master... CD-ROM Drive",
    "",
    "Plug and Play BIOS Extension v1.0A  (C) EazyCorp",
    "PnP Init Completed",
]

for line in post_lines:
    tk.Label(main_frame, text=line,
             bg=WIN98_BLACK, fg=WIN98_GRAY,
             font=FONT_SMALL, anchor="w").pack(fill="x", padx=20)

# ── LOGO (Win98 cloud logo area) ──────────────────────────────
logo_frame = tk.Frame(main_frame, bg=WIN98_BLACK, pady=20)
logo_frame.pack()

try:
    img = Image.open("python-logo.png").resize((120, 120), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(img, master=root)
    img_label = tk.Label(logo_frame, image=tk_img, bg=WIN98_BLACK,
                         relief="flat", bd=0)
    img_label.image = tk_img
    img_label.pack()
except Exception:
    tk.Label(logo_frame, text="[EazyOS]", bg=WIN98_BLACK,
             fg=WIN98_YELLOW, font=FONT_TITLE).pack()

# ── LOADING TEXT ───────────────────────────────────────────────
tk.Label(main_frame,
         text="Starting EazyOS...",
         bg=WIN98_BLACK, fg=WIN98_WHITE,
         font=("Courier New", 14, "bold")).pack(pady=(10, 2))

# ── PROGRESS BAR  (Win98 style – solid colour blocks) ─────────
pb_outer = tk.Frame(main_frame, bg=WIN98_GRAY,
                    bd=2, relief="sunken", padx=2, pady=2)
pb_outer.pack(pady=8, padx=60, fill="x")

pb_inner = tk.Frame(pb_outer, bg=WIN98_DARK, height=18, width=0)
pb_inner.pack(side="left")

pb_label = tk.Label(pb_outer, text="  0%",
                    bg=WIN98_GRAY, fg=WIN98_BLACK,
                    font=FONT_SMALL)
pb_label.pack(side="right", padx=4)

# ── SPINNER ────────────────────────────────────────────────────
spinner_label = tk.Label(main_frame, text="|",
                         bg=WIN98_BLACK, fg=WIN98_YELLOW,
                         font=FONT_SPINNER)
spinner_label.pack(pady=4)

# ── STATUS LINE (bottom) ───────────────────────────────────────
status_frame = tk.Frame(root, bg=WIN98_DARK, pady=3)
status_frame.pack(fill="x", side="bottom")

status_var = tk.StringVar(value="Initializing hardware...")
tk.Label(status_frame, textvariable=status_var,
         bg=WIN98_DARK, fg=WIN98_WHITE,
         font=FONT_SMALL).pack(side="left", padx=10)

clock_var = tk.StringVar()
clock_label = tk.Label(status_frame, textvariable=clock_var,
                       bg=WIN98_DARK, fg=WIN98_WHITE,
                       font=FONT_SMALL)
clock_label.pack(side="right", padx=10)

def update_clock():
    clock_var.set(time.strftime("%H:%M:%S"))
    root.after(1000, update_clock)
update_clock()

# ──────────────────────────────────────────────────────────────
# ANIMATION
# ──────────────────────────────────────────────────────────────
DURATION_MS = 10_000   # total boot time
frames      = ["|", "/", "-", "\\"]
frame_idx   = 0
done        = False
start_time  = time.time()

status_messages = [
    (0,    "Initializing hardware..."),
    (0.15, "Loading registry..."),
    (0.30, "Starting device drivers..."),
    (0.50, "Loading EazyOS kernel..."),
    (0.70, "Configuring network..."),
    (0.85, "Preparing desktop..."),
    (0.95, "Almost there..."),
]

def get_status(pct):
    msg = status_messages[0][1]
    for threshold, text in status_messages:
        if pct >= threshold:
            msg = text
    return msg

def animate():
    global frame_idx, done

    elapsed = (time.time() - start_time)
    pct     = min(elapsed / (DURATION_MS / 1000), 1.0)

    # Spinner
    spinner_label.config(text=frames[frame_idx])
    frame_idx = (frame_idx + 1) % len(frames)

    # Progress bar – get total width from outer frame
    total_w = pb_outer.winfo_width() - pb_label.winfo_width() - 8
    bar_w   = max(0, int(total_w * pct))
    pb_inner.config(width=bar_w)
    pb_label.config(text=f"  {int(pct * 100)}%")

    # Status
    status_var.set(get_status(pct))

    if not done:
        root.after(100, animate)
    else:
        spinner_label.config(text="✓", fg="#00FF00")
        status_var.set("Boot complete. Launching login...")
        root.after(800, launch_login)

def launch_login():
    root.destroy()
    subprocess.run([sys.executable, "login.py"])

animate()

# ── Key bindings ───────────────────────────────────────────────
def on_key_press(event):
    import os

    if event.keysym == "F8":
        try:
            os.startfile("bios.py")
        except Exception:
            subprocess.Popen([sys.executable, "bios.py"])
        root.destroy()

    elif event.keysym == "F6":
        try:
            
            os.startfile("boot\safemode\os\login.py")
        except Exception:
            
            subprocess.Popen([sys.executable, "boot\safemode\login.py"])
        root.destroy()

root.bind("<Key>", on_key_press)

def finish():
    global done
    done = True

root.after(DURATION_MS, finish)
root.mainloop()
