import os
import sys
from datetime import datetime
import subprocess

def show_welcome():
    print("Eazy OS [3.2 Pre-Release Version 1]")
    print("Made Possible By Python 3.14.5 (c) The Python Software Foundation. All rights reserved.")
    print("Type 'help' for a list of commands. Type 'exit' to quit.\n")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==========================================
# PATH CONFIGURATION
# ==========================================
# BASE_DIR pinpoints the exact directory where THIS script is running from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# COMMAND HANDLERS
# ==========================================

def cmd_help(args):
    print("""
=============================
Available commands:
=============================
  help         - Show this help message
  exit         - Exits CMD
  clear        - Clear the screen
  ls / dir     - List files in current directory
  cd [dir]     - Change directory
  pwd          - Print current directory
  echo [msg]   - Print a message
  run [file]   - Run a Python script
  about        - Show info about CMD
  time         - Shows the time
  update       - Run Update Script
  usrmgr       - Run Credential Manager
  control      - Run Control Panel
  regedit      - Run Regedit
=============================  
""")

def cmd_exit(args):
    print("Exiting CMD...")
    clear_screen()
    sys.exit(0)

def cmd_clear(args):
    clear_screen()

def cmd_ls(args):
    try:
        for item in os.listdir():
            print(item)
    except Exception as e:
        print(f"Error listing directory: {e}")

def cmd_cd(args):
    if not args:
        print(os.getcwd())
        return
    
    path = " ".join(args)
    try:
        os.chdir(path)
        print(f"Changed directory to: {os.getcwd()}")
    except FileNotFoundError:
        print("Directory not found.")
    except Exception as e:
        print(f"Error: {e}")

def cmd_pwd(args):
    print(os.getcwd())

def cmd_echo(args):
    print(" ".join(args))

def cmd_time(args):
    print(f"Current Date and Time: {datetime.now()}")

def cmd_about(args):
    print("CMD version: [3.2]")
    print("Made Possible By: Python 3.14.5")
    print("Copyright: (c) The Python Software Foundation. All rights reserved.")

# --- System Script Launchers (Using Absolute Paths) ---

def _run_sub_script(relative_path, success_msg, error_msg, use_popen=False, new_window=False):
    """
    Helper to safely launch external scripts using absolute paths.
    Can open batch files in a brand new window.
    """
    absolute_path = os.path.join(BASE_DIR, relative_path)
    
    if not os.path.exists(absolute_path):
        print(f"Error: {error_msg}")
        return

    try:
        # Check if we need to launch a batch file in a new window
        if absolute_path.endswith('.bat') and new_window:
            # "start" is a shell command, so we use shell=True and Popen to keep it non-blocking
            subprocess.Popen(f'start "" "{absolute_path}"', shell=True)
        else:
            cmd = [absolute_path] if absolute_path.endswith('.bat') else [sys.executable, absolute_path]
            if use_popen:
                subprocess.Popen(cmd)
            else:
                subprocess.run(cmd)
                
        print(success_msg)
    except Exception as e:
        print(f"Failed to launch application: {e}")
def cmd_update(args):
    _run_sub_script(
        relative_path=os.path.join("setup", "UPDATEOS.py"), 
        success_msg="EazyOS Update Script Successfully Opened", 
        error_msg="EazyOS Update Script could not be located!"
    )

def cmd_regedit(args):
    _run_sub_script(
        relative_path=os.path.join("SYSTEM", "regedit.py"), 
        success_msg="Regedit Successfully Opened", 
        error_msg="Regedit Script could not be located!"
    )

def cmd_control(args):
    _run_sub_script(
        relative_path="control.py", 
        success_msg="Control Panel Successfully Opened", 
        error_msg="Control Panel could not be located!"
    )

def cmd_usrmgr(args):
    _run_sub_script(
        relative_path=os.path.join("SYSTEM", "user.bat"), 
        success_msg="Credential Manager Successfully Opened in a new window.", 
        error_msg="Credential Manager could not be located!", 
        new_window=True
    )

def cmd_run(args):
    if not args:
        print("Usage: run [filename.py]")
        return
    
    filename = " ".join(args)
    
    # For user 'run' files, we intentionally check the CURRENT directory first,
    # then fallback to the BASE_DIR if it's a global utility file.
    if os.path.isfile(filename):
        target_file = os.path.abspath(filename)
    elif os.path.isfile(os.path.join(BASE_DIR, filename)):
        target_file = os.path.join(BASE_DIR, filename)
    else:
        print(f"File not found: {filename}")
        return

    print(f"Running {target_file}...\n")
    try:
        subprocess.run([sys.executable, target_file])
    except Exception as e:
        print(f"Error executing script: {e}")

# ==========================================
# COMMAND REGISTRY MAP
# ==========================================
COMMANDS = {
    "help": cmd_help,
    "exit": cmd_exit,
    "clear": cmd_clear,
    "ls": cmd_ls,
    "dir": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "echo": cmd_echo,
    "time": cmd_time,
    "about": cmd_about,
    "update": cmd_update,
    "regedit": cmd_regedit,
    "control": cmd_control,
    "usrmgr": cmd_usrmgr,
    "run": cmd_run
}

# ==========================================
# MAIN EXECUTION LOOP
# ==========================================
def main():
    clear_screen()
    show_welcome()

    while True:
        try:
            user_input = input(f"{os.getcwd()}> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            cmd_name = parts[0].lower()
            args = parts[1:]

            if cmd_name in COMMANDS:
                COMMANDS[cmd_name](args)
            else:
                print(f"Unknown command: {cmd_name}. Type 'help' for a list of commands.")
        
        except KeyboardInterrupt:
            print("\nType 'exit' to quit.")
        except Exception as e:
            print(f"An unexpected shell error occurred: {e}")

if __name__ == "__main__":
    main()
