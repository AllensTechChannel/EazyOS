import tkinter as tk
from tkinter import filedialog
import time
import threading
import os
import sys

if sys.platform == "win32":
    import winsound
else:
    winsound = None

BG          = "#c0c0c0"
DARK_BORDER = "#808080"
TITLE_BG    = "#000080"
TITLE_FG    = "#ffffff"
SCREEN_BG   = "#000000"
LED_RED     = "#ff4400"
LED_GREEN   = "#00bb00"
BTN_BG      = "#c0c0c0"


def win98_button(parent, text, command, width=8):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=BTN_BG, fg="#000000",
        relief="raised", bd=2,
        activebackground="#d4d0c8",
        font=("MS Sans Serif", 8),
        width=width, cursor="arrow",
    )
    btn.bind("<ButtonPress-1>",   lambda e: btn.config(relief="sunken"))
    btn.bind("<ButtonRelease-1>", lambda e: btn.config(relief="raised"))
    return btn

def win98_label(parent, text="", font=None, fg="#000000", bg=BG, **kw):
    return tk.Label(parent, text=text,
                    font=font or ("MS Sans Serif", 8),
                    fg=fg, bg=bg, **kw)

def win98_spinbox(parent, from_, to, width=3, textvariable=None):
    return tk.Spinbox(
        parent, from_=from_, to=to, width=width,
        textvariable=textvariable,
        bg="#ffffff", fg="#000000",
        relief="sunken", bd=2,
        font=("MS Sans Serif", 9),
        buttonbackground=BTN_BG,
        wrap=True,
    )


class Win98Clock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.overrideredirect(True)

        self._drag_x = 0
        self._drag_y = 0

        self.alarm_hour   = tk.StringVar(value="12")
        self.alarm_min    = tk.StringVar(value="00")
        self.alarm_ampm   = tk.StringVar(value="AM")
        self.alarm_set    = False
        self.alarm_firing = False

        # _stop_alarm tells the loop thread to exit
        self._stop_alarm  = threading.Event()

        # Sound mode — can be changed ANY TIME, even while alarm is firing
        self.sound_mode = tk.StringVar(value="beep")
        default_wav = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.wav")
        self.wav_path = tk.StringVar(value=default_wav)

        self._build_ui()
        self._tick()

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = self.winfo_width()
        h  = self.winfo_height()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        outer = tk.Frame(self, bg=BG, bd=2, relief="raised")
        outer.pack(padx=2, pady=2)

        # Title bar
        titlebar = tk.Frame(outer, bg=TITLE_BG, height=20)
        titlebar.pack(fill="x")
        titlebar.bind("<ButtonPress-1>", self._start_drag)
        titlebar.bind("<B1-Motion>",     self._do_drag)

        icon_lbl = tk.Label(titlebar, text="[*]", bg=TITLE_BG, fg=TITLE_FG,
                            font=("MS Sans Serif", 9))
        icon_lbl.pack(side="left", padx=(4, 2), pady=1)
        icon_lbl.bind("<ButtonPress-1>", self._start_drag)
        icon_lbl.bind("<B1-Motion>",     self._do_drag)

        title_lbl = tk.Label(titlebar, text="Alarm Clock",
                             bg=TITLE_BG, fg=TITLE_FG,
                             font=("MS Sans Serif", 8, "bold"))
        title_lbl.pack(side="left", pady=1)
        title_lbl.bind("<ButtonPress-1>", self._start_drag)
        title_lbl.bind("<B1-Motion>",     self._do_drag)

        close_btn = tk.Button(
            titlebar, text="X", command=self._on_close,
            bg=BTN_BG, fg="#000000", relief="raised", bd=2,
            font=("MS Sans Serif", 7, "bold"),
            width=2, height=1, cursor="arrow",
            activebackground="#ff0000", activeforeground="#ffffff",
        )
        close_btn.pack(side="right", padx=2, pady=2)

        body = tk.Frame(outer, bg=BG, padx=8, pady=6)
        body.pack(fill="both")

        # LED screen
        screen_frame = tk.Frame(body, bg=DARK_BORDER, bd=2, relief="sunken")
        screen_frame.pack(fill="x", pady=(0, 6))
        screen_inner = tk.Frame(screen_frame, bg=SCREEN_BG, padx=10, pady=6)
        screen_inner.pack(fill="both")

        self.time_lbl = tk.Label(screen_inner, text="12:00:00",
                                 bg=SCREEN_BG, fg=LED_RED,
                                 font=("Courier New", 36, "bold"))
        self.time_lbl.pack()

        bottom_row = tk.Frame(screen_inner, bg=SCREEN_BG)
        bottom_row.pack(fill="x")

        self.ampm_lbl = tk.Label(bottom_row, text="AM",
                                 bg=SCREEN_BG, fg=LED_RED,
                                 font=("Courier New", 14, "bold"))
        self.ampm_lbl.pack(side="left")

        self.date_lbl = tk.Label(bottom_row, text="",
                                 bg=SCREEN_BG, fg=LED_GREEN,
                                 font=("Courier New", 11))
        self.date_lbl.pack(side="right")

        self.alarm_ind = tk.Label(screen_inner, text="",
                                  bg=SCREEN_BG, fg=LED_RED,
                                  font=("MS Sans Serif", 7))
        self.alarm_ind.pack(anchor="e")

        # Separator
        tk.Frame(body, bg=DARK_BORDER, height=2).pack(fill="x", pady=(0, 6))

        # Alarm time row
        alarm_row = tk.Frame(body, bg=BG)
        alarm_row.pack(fill="x", pady=(0, 4))

        win98_label(alarm_row, "Set Alarm:").pack(side="left", padx=(0, 6))
        self.hour_sb = win98_spinbox(alarm_row, 1, 12, width=3,
                                     textvariable=self.alarm_hour)
        self.hour_sb.pack(side="left")
        win98_label(alarm_row, ":").pack(side="left")
        self.min_sb = win98_spinbox(alarm_row, 0, 59, width=3,
                                    textvariable=self.alarm_min)
        self.min_sb.pack(side="left")
        self.ampm_btn = win98_button(alarm_row, "AM", self._toggle_ampm, width=4)
        self.ampm_btn.pack(side="left", padx=(4, 0))

        # Sound group box
        tk.Frame(body, bg=DARK_BORDER, height=1).pack(fill="x", pady=(2, 4))

        sound_frame = tk.LabelFrame(body, text=" Sound ", bg=BG, fg="#000000",
                                    font=("MS Sans Serif", 8), bd=2, relief="groove")
        sound_frame.pack(fill="x", pady=(0, 4))

        mode_row = tk.Frame(sound_frame, bg=BG)
        mode_row.pack(fill="x", padx=4, pady=(4, 2))

        self.rb_beep = tk.Radiobutton(
            mode_row, text="Beep", variable=self.sound_mode,
            value="beep", bg=BG, fg="#000000",
            font=("MS Sans Serif", 8), activebackground=BG,
            command=self._on_mode_change)
        self.rb_beep.pack(side="left")

        self.rb_wav = tk.Radiobutton(
            mode_row, text="WAV file", variable=self.sound_mode,
            value="wav", bg=BG, fg="#000000",
            font=("MS Sans Serif", 8), activebackground=BG,
            command=self._on_mode_change)
        self.rb_wav.pack(side="left", padx=(10, 0))

        wav_row = tk.Frame(sound_frame, bg=BG)
        wav_row.pack(fill="x", padx=4, pady=(0, 4))

        self.wav_entry = tk.Entry(
            wav_row, textvariable=self.wav_path,
            bg="#ffffff", fg="#000000",
            relief="sunken", bd=2,
            font=("MS Sans Serif", 7),
            width=28, state="disabled",
        )
        self.wav_entry.pack(side="left", padx=(0, 4))

        self.browse_btn = win98_button(wav_row, "Browse...", self._browse_wav, width=8)
        self.browse_btn.pack(side="left")
        self.browse_btn.config(state="disabled")

        # Action buttons
        tk.Frame(body, bg=DARK_BORDER, height=1).pack(fill="x", pady=(2, 4))

        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack()

        self.set_btn = win98_button(btn_row, "Set Alarm", self._set_alarm,   width=10)
        self.set_btn.pack(side="left", padx=3)
        self.clr_btn = win98_button(btn_row, "Clear",     self._clear_alarm, width=6)
        self.clr_btn.pack(side="left", padx=3)
        self.snz_btn = win98_button(btn_row, "Snooze",    self._snooze,      width=7)
        self.snz_btn.pack(side="left", padx=3)
        self.snz_btn.config(state="disabled")

        # Status bar
        self.status_lbl = tk.Label(
            body, text="No alarm set.",
            bg=BG, fg="#000000",
            font=("MS Sans Serif", 8),
            anchor="w", bd=1, relief="sunken",
        )
        self.status_lbl.pack(fill="x", pady=(6, 0), ipady=2)

    # --------------------------------------------------------- sound mode ---
    def _on_mode_change(self):
        """Enable/disable WAV controls when radio button changes."""
        if self.sound_mode.get() == "wav":
            self.wav_entry.config(state="normal")
            self.browse_btn.config(state="normal")
        else:
            self.wav_entry.config(state="disabled")
            self.browse_btn.config(state="disabled")

    def _browse_wav(self):
        path = filedialog.askopenfilename(
            title="Select WAV file",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if path:
            self.wav_path.set(path)

    # --------------------------------------------------------------- drag ---
    def _start_drag(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _do_drag(self, e):
        self.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    # --------------------------------------------------------------- tick ---
    def _tick(self):
        now  = time.localtime()
        h24  = now.tm_hour
        m    = now.tm_min
        s    = now.tm_sec
        ampm = "AM" if h24 < 12 else "PM"
        h12  = h24 % 12 or 12

        self.time_lbl.config(text=f"{h12:02d}:{m:02d}:{s:02d}")
        self.ampm_lbl.config(text=ampm)

        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        mons = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]
        self.date_lbl.config(
            text=f"{days[now.tm_wday]} {mons[now.tm_mon-1]} {now.tm_mday:02d} {now.tm_year}"
        )

        if self.alarm_set and not self.alarm_firing:
            ah   = int(self.alarm_hour.get())
            am_  = int(self.alarm_min.get())
            aap  = self.alarm_ampm.get()
            ah24 = ah % 12 + (12 if aap == "PM" else 0)
            if h24 == ah24 and m == am_ and s == 0:
                self._fire_alarm()

        if self.alarm_firing:
            cur = self.alarm_ind.cget("text")
            self.alarm_ind.config(text="" if cur else "*** ALARM ***")

        self.after(1000, self._tick)

    # --------------------------------------------------- sound loop thread ---
    def _play_one_cycle(self):
        """
        Play one cycle of the currently selected sound.
        Re-reads self.sound_mode and self.wav_path every call so the user
        can switch modes even while the alarm is ringing.
        Returns when one cycle is done OR _stop_alarm is set.
        """
        if self.sound_mode.get() == "wav":
            wav = self.wav_path.get()
            if os.path.isfile(wav):
                if sys.platform == "win32":
                    # SND_FILENAME blocks until the file finishes — perfect for looping
                    winsound.PlaySound(wav, winsound.SND_FILENAME)
                else:
                    import subprocess, shutil
                    player = next((p for p in ["afplay", "aplay", "paplay"]
                                   if shutil.which(p)), None)
                    if player:
                        proc = subprocess.Popen([player, wav])
                        while proc.poll() is None:
                            if self._stop_alarm.is_set():
                                proc.terminate()
                                return
                            time.sleep(0.05)
                    else:
                        print("\a", end="", flush=True)
                        time.sleep(1)
                return  # one WAV cycle done

        # ---- Beep mode (also fallback when WAV file is missing) ----
        if sys.platform == "win32":
            for freq, dur in [(880,200),(660,200),(880,200),(660,200),(880,300)]:
                if self._stop_alarm.is_set():
                    return
                winsound.Beep(freq, dur)
                time.sleep(0.05)
            time.sleep(0.4)
        else:
            print("\a", end="", flush=True)
            time.sleep(0.5)

    def _play_loop(self):
        """Background thread: keep playing cycles until _stop_alarm is set."""
        self._stop_alarm.clear()
        while not self._stop_alarm.is_set():
            self._play_one_cycle()

    # --------------------------------------------------------- alarm logic ---
    def _toggle_ampm(self):
        new = "PM" if self.alarm_ampm.get() == "AM" else "AM"
        self.alarm_ampm.set(new)
        self.ampm_btn.config(text=new)

    def _set_alarm(self):
        try:
            h = int(self.alarm_hour.get())
            m = int(self.alarm_min.get())
            assert 1 <= h <= 12 and 0 <= m <= 59
        except Exception:
            self.status_lbl.config(text="Invalid time! Use H:MM (1-12).")
            return

        self._stop_sound()
        self.alarm_min.set(f"{m:02d}")
        self.alarm_set    = True
        self.alarm_firing = False
        self.snz_btn.config(state="disabled")
        ap   = self.alarm_ampm.get()
        mode = "WAV" if self.sound_mode.get() == "wav" else "Beep"
        self.alarm_ind.config(text=f"ALARM {h:02d}:{m:02d} {ap}")
        self.status_lbl.config(text=f"Alarm set for {h:02d}:{m:02d} {ap}  [{mode}]")

    def _clear_alarm(self):
        self._stop_sound()
        self.alarm_set    = False
        self.alarm_firing = False
        self.alarm_ind.config(text="")
        self.snz_btn.config(state="disabled")
        self.status_lbl.config(text="No alarm set.")

    def _fire_alarm(self):
        self.alarm_firing = True
        self.snz_btn.config(state="normal")
        self.status_lbl.config(text="  *** WAKE UP! ***  ")
        threading.Thread(target=self._play_loop, daemon=True).start()

    def _stop_sound(self):
        """Signal the loop thread to stop, and silence any playing WAV."""
        self._stop_alarm.set()
        if sys.platform == "win32" and winsound:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def _snooze(self):
        self._stop_sound()
        self.alarm_firing = False
        now   = time.localtime()
        total = now.tm_hour * 60 + now.tm_min + 5
        sh24  = (total // 60) % 24
        sm    = total % 60
        sap   = "PM" if sh24 >= 12 else "AM"
        sh12  = sh24 % 12 or 12

        self.alarm_hour.set(str(sh12))
        self.alarm_min.set(f"{sm:02d}")
        self.alarm_ampm.set(sap)
        self.ampm_btn.config(text=sap)
        self.alarm_set = True
        self.alarm_ind.config(text=f"ZZZ {sh12:02d}:{sm:02d} {sap}")
        self.snz_btn.config(state="disabled")
        self.status_lbl.config(text=f"Snoozed until {sh12:02d}:{sm:02d} {sap}")

    def _on_close(self):
        self._stop_sound()
        self.destroy()


if __name__ == "__main__":
    app = Win98Clock()
    app.mainloop()