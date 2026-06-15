import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import winsound
import os
import logging

# === LOGGING SETUP ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eazyos_login.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === PATH CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join("media")


# === CONSTANTS ===
WIN98_BLUE = "#000080"
WIN98_GRAY = "#C0C0C0"
WIN98_DARK_GRAY = "#808080"

# === CONFIGURATION ===
ENABLE_SOUNDS = False  # Set to False to disable sounds


class SoundManager:
    """Centralized sound management"""
    
    @staticmethod
    def play(filename: str, async_play: bool = False) -> None:
        """Play a sound file safely"""
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


class Win98MessageBox:
    """Windows 98-style message boxes"""
    
    @staticmethod
    def showinfo(parent, title: str, message: str) -> None:
        """Show an info message"""
        Win98MessageBox._create_messagebox(parent, "info", title, message)
    
    @staticmethod
    def showerror(parent, title: str, message: str) -> None:
        """Show an error message"""
        Win98MessageBox._create_messagebox(parent, "error", title, message)
    
    @staticmethod
    def _create_messagebox(parent, msg_type: str, title: str, message: str) -> None:
        """Create a Windows 98-style message dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.configure(bg=WIN98_GRAY)
        dialog.resizable(False, False)
        
        # Calculate size and position
        dialog_width = 380
        dialog_height = 140
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        # Center on parent
        x = parent_x + (parent_w - dialog_width) // 2
        y = parent_y + (parent_h - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Content frame
        content = tk.Frame(dialog, bg=WIN98_GRAY, relief="ridge", bd=4)
        content.pack(fill="both", expand=True)
        
        # Icon and message area
        msg_frame = tk.Frame(content, bg=WIN98_GRAY)
        msg_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Icon (left side)
        icon_label = tk.Label(msg_frame, bg=WIN98_GRAY, font=("MS Sans Serif", 28))
        icon_label.pack(side="left", padx=(0, 15))
        
        # Set icon based on message type
        if msg_type == "info":
            icon_label.config(text="ℹ", fg="#0000FF")
        elif msg_type == "error":
            icon_label.config(text="✖", fg="#FF0000")
        
        # Message text (right side)
        msg_label = tk.Label(
            msg_frame,
            text=message,
            bg=WIN98_GRAY,
            fg="black",
            font=("MS Sans Serif", 9),
            justify="left",
            wraplength=250,
            anchor="w"
        )
        msg_label.pack(side="left", fill="both", expand=True)
        
        # Button frame
        btn_frame = tk.Frame(content, bg=WIN98_GRAY)
        btn_frame.pack(side="bottom", pady=(5, 15))
        
        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            try:
                dialog.destroy()
            except:
                pass
        
        # OK button
        ok_btn = tk.Button(
            btn_frame,
            text="OK",
            width=10,
            height=1,
            bg=WIN98_GRAY,
            fg="black",
            font=("MS Sans Serif", 8, "bold"),
            relief="raised",
            bd=2,
            activebackground="#DFDFDF",
            activeforeground="black",
            command=close_dialog,
            cursor="hand2"
        )
        ok_btn.pack(padx=5)
        
        # Bind Enter and Escape
        dialog.bind("<Return>", lambda e: close_dialog())
        dialog.bind("<Escape>", lambda e: close_dialog())
        
        # Focus after a moment
        dialog.after(100, lambda: ok_btn.focus_set())
        
        # Play system sound
        if ENABLE_SOUNDS:
            try:
                if msg_type == "error":
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
        
        # Make modal
        dialog.transient(parent)
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        
        # Center on parent and show
        dialog.update_idletasks()
        
        # Wait for dialog to close
        try:
            dialog.wait_window(dialog)
        except:
            pass


class LoginWindow:
    """EazyOS Login Window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EazyOS Logon")
        self.root.resizable(False, False)
        self.root.configure(bg=WIN98_GRAY)
        
        # Load credentials
        self.stored_username, self.stored_password = self._load_credentials()
        
        # Setup window
        self._setup_window()
        self._create_ui()
        self._bind_shortcuts()
        
        logger.info("Login window initialized")
    
    def _setup_window(self):
        """Configure window size and position"""
        WIDTH, HEIGHT = 360, 220
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WIDTH) // 2
        y = (screen_h - HEIGHT) // 2
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")
    
    def _load_credentials(self):
        """Load credentials from file"""
        try:
            credentials_path = os.path.abspath(
                os.path.join("credentials.txt")
            )

            if not os.path.exists(credentials_path):
                logger.error("Credentials file not found")
                return None, None

            with open(credentials_path, "r") as f:
                line = f.readline().strip()

                if "," in line:
                    username, password = line.split(",", 1)
                    username = username.strip()
                    password = password.strip()
                    logger.info(f"Credentials loaded for user: {username}")
                    return username, password
                else:
                    logger.error("Invalid credentials file format")
                    return None, None

        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None, None
    def _create_ui(self):
        """Create the login UI"""
        # Main beveled frame
        outer = tk.Frame(self.root, bg=WIN98_DARK_GRAY, bd=2, relief="raised")
        outer.pack(fill="both", expand=True, padx=6, pady=6)
        
        inner = tk.Frame(outer, bg=WIN98_GRAY, bd=2, relief="sunken")
        inner.pack(fill="both", expand=True)
        
        font98 = ("MS Sans Serif", 9)
        
        # Title bar
        tk.Label(
            inner,
            text="Enter Network Password",
            bg=WIN98_BLUE,
            fg="white",
            font=("MS Sans Serif", 9, "bold"),
            anchor="w",
            padx=6
        ).pack(fill="x")
        
        # Content area
        content = tk.Frame(inner, bg=WIN98_GRAY)
        content.pack(padx=12, pady=14)
        
        # Username
        tk.Label(
            content,
            text="User name:",
            bg=WIN98_GRAY,
            font=font98
        ).grid(row=0, column=0, sticky="e", pady=4)
        
        self.username_entry = tk.Entry(content, font=font98, relief="sunken", bd=2)
        self.username_entry.grid(row=0, column=1, pady=4)
        
        # Password
        tk.Label(
            content,
            text="Password:",
            bg=WIN98_GRAY,
            font=font98
        ).grid(row=1, column=0, sticky="e", pady=4)
        
        self.password_entry = tk.Entry(content, show="*", font=font98, relief="sunken", bd=2)
        self.password_entry.grid(row=1, column=1, pady=4)
        
        # Buttons
        btn_frame = tk.Frame(inner, bg=WIN98_GRAY)
        btn_frame.pack(pady=6)
        
        login_btn = tk.Button(
            btn_frame,
            text="OK",
            width=8,
            font=font98,
            relief="raised",
            bd=2,
            bg=WIN98_GRAY,
            command=self._validate_and_login
        )
        login_btn.grid(row=0, column=0, padx=6)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            width=8,
            font=font98,
            relief="raised",
            bd=2,
            bg=WIN98_GRAY,
            command=self._exit
        )
        cancel_btn.grid(row=0, column=1, padx=6)
        
        # Focus on username
        self.username_entry.focus_set()
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind("<Control-Shift-B>", lambda e: self._trigger_bsod())
        self.root.bind("<Escape>", lambda e: self._exit())
        self.root.bind("<Return>", lambda e: self._validate_and_login())
    
    def _validate_and_login(self):
        """Validate credentials and login"""
        # Check if credentials were loaded
        if self.stored_username is None or self.stored_password is None:
            Win98MessageBox.showerror(
                self.root,
                "Error",
                "Credentials file not found or invalid."
            )
            return
        
        userid = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if userid == self.stored_username and password == self.stored_password:
            logger.info(f"Login successful for user: {userid}")
            Win98MessageBox.showinfo(
                self.root,
                "Welcome",
                f"Welcome, {self.stored_username}"
            )
            self._restart_to_desktop()
        else:
            logger.warning(f"Failed login attempt for user: {userid}")
            Win98MessageBox.showerror(
                self.root,
                "Logon Failed",
                "Invalid user name or password"
            )
            # Clear password field
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
    
    def _restart_to_desktop(self):
        """Close login and start desktop"""
        try:
            self.root.destroy()
            desktop_script = os.path.join(BASE_DIR, "OS.py")
            
            if os.path.exists(desktop_script):
                subprocess.run([sys.executable, desktop_script])
            else:
                logger.error(f"Desktop script not found: {desktop_script}")
        except Exception as e:
            logger.error(f"Failed to start desktop: {e}")
    
    def _trigger_bsod(self):
        """Trigger BSOD and exit"""
        try:
            bsod_script = os.path.join(BASE_DIR, "bsod.py")
            if os.path.exists(bsod_script):
                subprocess.run([sys.executable, bsod_script])
                self.root.after(150, self._exit)
            else:
                logger.error(f"BSOD script not found: {bsod_script}")
        except Exception as e:
            logger.error(f"Failed to trigger BSOD: {e}")
    
    def _exit(self):
        """Exit the application"""
        logger.info("Login window closed")
        self.root.destroy()
    
    def run(self):
        """Start the main loop"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Login interrupted by user")
            self._exit()


# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    try:
        login = LoginWindow()
        login.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        messagebox.showerror("Fatal Error", f"Login encountered a critical error:\n{e}")
        sys.exit(1)
