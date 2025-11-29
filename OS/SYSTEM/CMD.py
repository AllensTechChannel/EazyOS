import os
import winsound
from datetime import datetime
def python_cmd():
    print("Eazy OS [2.1.0] (c) The Python Software Foundation. All rights reserved.")
    print("Type 'help' for a list of commands. Type 'exit' to quit.\n")

# Base directory where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper function to play sound from the media folder
def play_sound(filename):
    path = os.path.join(BASE_DIR, 'media', filename)
    if os.path.exists(path):
        winsound.PlaySound(path, winsound.SND_FILENAME)
    else:
        print(f"[Sound file not found: {path}]")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

python_cmd()

while True:
        command = input(f"{os.getcwd()}> ").strip()

        if command.lower() == "exit":
            print("Exiting CMD...")
            clear_screen()
            break

        elif command.lower() == "help":
            print("""
Available commands:
  help         - Show this help message
  exit         - Exit the CMD
  clear        - Clear the screen
  ls / dir     - List files in current directory
  cd [dir]     - Change directory
  pwd          - Print current directory
  echo [msg]   - Print a message
  run [file]   - Run a Python script
  about        - Show info about CMD
  time         - Shows the time
  nyan         - Plays nyan_cat!_official.wav 
  weezer       - Plays get-weezerd.wav
""")

        elif command.lower() in ["ls", "dir"]:
            for item in os.listdir():
                print(item)

        elif command.lower().startswith("cd "):
            path = command[3:].strip()
            try:
                os.chdir(path)
                print(f"Changed directory to: {os.getcwd()}")
                play_sound('error-beep.wav')
            except FileNotFoundError:
                print("Directory not found.")
                play_sound('error-beep.wav')

        elif command.lower() == "pwd":
            print(os.getcwd())
        elif command.lower() == "about":
            print("CMD version: [2.1.0]")
            print("Copy Right: (c) The Python Software Foundation. All rights reserved.")
        elif command.lower() == "time":  
            current_datetime = datetime.now()

            # Print the full date and time
            print(f"Current Date and Time: {current_datetime}")
        elif command.lower() == "nyan": 
            winsound.PlaySound(os.path.join(BASE_DIR,'nyan_cat!_official.wav'), winsound.SND_FILENAME)
            winsound.PlaySound(None, winsound.SND_PURGE)
             
        elif command.lower() == "weezer": 
            winsound.PlaySound(os.path.join(BASE_DIR,'get-weezerd.wav'), winsound.SND_FILENAME)
            winsound.PlaySound(None, winsound.SND_PURGE)
        
        elif command.lower().startswith("echo "):
            print(command[5:].strip())

        elif command.lower() == "clear":
            clear_screen()

        elif command.lower().startswith("run "):
            filename = command[4:].strip()
            if os.path.isfile(filename):
                try:
                    with open(filename, "r") as f:
                        code = f.read()
                        print(f"Running {filename}...\n")
                        exec(code, globals())
                except Exception as e:
                    print(f"Error running {filename}: {e}")
                    play_sound('error-beep.wav')
            else:
                print(f"File not found: {filename}")
                play_sound('error-beep.wav')

        else:
            print(f"Unknown command: {command}. Type 'help' for a list of commands.")
            play_sound('error-beep.wav')

# Run it
if __name__ == "__main__":
    clear_screen()
    play_sound('error-beep.wav')
   

