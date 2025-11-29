import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import ctypes

def main():
    root = tk.Tk()
    root.state("zoomed")  
    root.configure(bg="white")
    canvas = tk.Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- Taskbar control (Windows only) ---
    def hide_taskbar():
        taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        if taskbar:
            ctypes.windll.user32.ShowWindow(taskbar, 0)  # SW_HIDE

    def show_taskbar():
        taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
        if taskbar:
            ctypes.windll.user32.ShowWindow(taskbar, 5)  # SW_SHOW

    # --- Program Launchers ---
    def open_google():
        try:
            root.withdraw()
            subprocess.Popen([sys.executable, r"internet explorer\google.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
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

    def open_DuckDuckGo():
        run_program(r"internet explorer\Duck.py")

    def open_internet():
        run_program(r"internet explorer\Custom.py")

    # --- Icon + Label Handling ---
    icons = []  # store references to prevent GC
    icon_start_x, icon_start_y, icon_spacing = 20, 20, 10

    def add_icon_with_label(image_path, command, text, x, y):
        try:
            icon_img = tk.PhotoImage(file=image_path)
            icons.append(icon_img)  # prevent garbage collection
            btn = tk.Button(root, image=icon_img, command=command, bd=0)
            canvas.create_window(x, y, anchor="nw", window=btn)
            lbl_y = y + icon_img.height() + 2
            lbl = tk.Label(root, text=text, bg="white", fg="black", font=("Helvetica", 10))
            canvas.create_window(x + icon_img.width() // 2, lbl_y, anchor="n", window=lbl)
            return icon_img.height() + lbl.winfo_reqheight() + icon_spacing
        except Exception as e:
            print(f"{text} icon not found:", e)
            return 0

    # --- Add Icons ---
    icon_start_y += add_icon_with_label("internet explorer\google.png", open_google, "Google", icon_start_x, icon_start_y)
    icon_start_y += add_icon_with_label("internet explorer\DuckDuckGo.png", open_DuckDuckGo, "DuckDuckGo", icon_start_x, icon_start_y)
    icon_start_y += add_icon_with_label("internet explorer\internet.png", open_internet, "Enter URL", icon_start_x, icon_start_y)

    root.mainloop()

# Only run if executed directly, not imported
if __name__ == "__main__":
    main()
