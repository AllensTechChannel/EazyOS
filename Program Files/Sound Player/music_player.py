import os
import time
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from pygame import mixer

# Initialize mixer
mixer.init()

# Global state
progress_slider_clicked = False

# Create main window
root = Tk()
root.title('Media Player')
root.geometry('700x500')
root.resizable(False, False)

# --- Background image (universal loader) ---
bg_path = os.path.join(os.path.dirname(__file__), "bg.jpg")  # look in same folder as script

if os.path.exists(bg_path):
    bg_image = Image.open(bg_path).resize((700, 500), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = Canvas(root, width=700, height=500)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
else:
    # fallback if image not found
    canvas = Canvas(root, width=700, height=500, bg="black")
    canvas.pack(fill="both", expand=True)

# --- Default music directory ---
music_dir = os.path.join(os.path.expanduser("~"), "Music")

# --- Styles ---
label_style = {
    'bg': '#282c34',
    'fg': '#61dafb',
    'font': ('Courier', 10, 'bold')
}
listbox_style = {
    'bg': '#1C1C1C',
    'fg': 'green',
    'font': ('Courier', 12),
    'selectbackground': '#696969',
    'selectforeground': 'black'
}

style = ttk.Style()
style.configure("TButton",
                font=('Courier', 12, 'bold'),
                background='#282c34',
                foreground='#61dafb',
                borderwidth=3,
                relief='raised')
style.map("TButton",
          background=[('active', '#444b58')],
          foreground=[('active', '#61dafb')])

style.configure("TScale",
                background="#282c34",
                troughcolor='#444b58',
                sliderrelief='raised')

# --- Playlist frame ---
listbox_frame = Frame(canvas, bg="black", bd=2, relief=SUNKEN)
listbox_frame.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.4)

scrollbar = Scrollbar(listbox_frame, orient=VERTICAL)
songs_list = Listbox(listbox_frame, selectmode=SINGLE,
                     yscrollcommand=scrollbar.set, **listbox_style)
scrollbar.config(command=songs_list.yview)
scrollbar.pack(side=RIGHT, fill=Y)
songs_list.pack(side=LEFT, fill=BOTH, expand=True)

# --- Functions ---
def show_info():
    messagebox.showinfo("Developer Info",
                        "Name: Rafi Ahamed\nEmail: fidaahamed15@gmail.com\nMusic Player App")

def add_songs():
    temp_song = filedialog.askopenfilenames(initialdir=music_dir,
                                            title="Choose a song",
                                            filetypes=[("mp3 Files", "*.mp3")])
    for s in temp_song:
        if s not in songs_list.get(0, END):
            songs_list.insert(END, s)

def delete_song():
    try:
        selected_song_index = songs_list.curselection()[0]
        songs_list.delete(selected_song_index)
    except IndexError:
        messagebox.showerror("Error", "No song selected to delete!")

def play_song():
    try:
        selected_song = songs_list.get(ACTIVE)
        mixer.music.load(selected_song)
        mixer.music.play()
        update_song_details()
    except Exception as e:
        messagebox.showerror("Error", f"Unable to play the song: {e}")

def control_playback(action):
    if action == 'pause':
        mixer.music.pause()
    elif action == 'resume':
        mixer.music.unpause()
    elif action == 'stop':
        mixer.music.stop()
        reset_progress()

def update_song_details():
    try:
        song_length = mixer.Sound(songs_list.get(ACTIVE)).get_length()
        progress_slider.config(to=song_length)
        total_time_label.config(
            text=f"Total Duration: {time.strftime('%M:%S', time.gmtime(song_length))}")

        def update():
            if mixer.music.get_busy():
                if not progress_slider_clicked:
                    current_time = mixer.music.get_pos() / 1000
                    progress_slider.set(current_time)
                    selected_time_label.config(
                        text=f"Selected Time: {time.strftime('%M:%S', time.gmtime(current_time))}")
                root.after(500, update)

        update()
    except Exception as e:
        print(f"Error: {e}")

def reset_progress():
    progress_slider.set(0)
    selected_time_label.config(text="Selected Time: 00:00")
    total_time_label.config(text="Total Duration: 00:00")

def on_progress_slider_click(event):
    global progress_slider_clicked
    progress_slider_clicked = True

def on_progress_slider_release(event):
    global progress_slider_clicked
    progress_slider_clicked = False
    seek_time = progress_slider.get()
    mixer.music.play(loops=0, start=seek_time)
    selected_time_label.config(
        text=f"Selected Time: {time.strftime('%M:%S', time.gmtime(seek_time))}")

# --- Widgets ---
selected_time_label = Label(canvas, text="Selected Time: 00:00", **label_style)
selected_time_label.place(relx=0.1, rely=0.6)

total_time_label = Label(canvas, text="Total Duration: 00:00", **label_style)
total_time_label.place(relx=0.7, rely=0.6)

progress_slider = ttk.Scale(canvas, from_=0, to=100, orient=HORIZONTAL, style="TScale")
progress_slider.place(relx=0.1, rely=0.65, relwidth=0.8)
progress_slider.bind("<Button-1>", on_progress_slider_click)
progress_slider.bind("<ButtonRelease-1>", on_progress_slider_release)

buttons = [
    {'text': 'Play', 'command': play_song},
    {'text': 'Pause', 'command': lambda: control_playback('pause')},
    {'text': 'Resume', 'command': lambda: control_playback('resume')},
    {'text': 'Stop', 'command': lambda: control_playback('stop')}
]
for i, btn in enumerate(buttons):
    ttk.Button(canvas, text=btn['text'], command=btn['command'],
               style="TButton").place(x=160 + i * 110, y=380)

volume_label = Label(canvas, text="Volume", **label_style)
volume_label.place(relx=0.85, rely=0.85, anchor="center")

volume_slider = ttk.Scale(canvas, from_=0, to=1, orient=HORIZONTAL, style="TScale",
                          command=lambda v: mixer.music.set_volume(float(v)))
volume_slider.set(0.5)
volume_slider.place(relx=0.85, rely=0.9, anchor="center", relwidth=0.15)

# --- Menus ---
my_menu = Menu(root)
root.config(menu=my_menu)

add_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="File", menu=add_song_menu)
add_song_menu.add_command(label="Add songs", command=add_songs)
add_song_menu.add_command(label="Delete song", command=delete_song)

info_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Info", menu=info_menu)
info_menu.add_command(label="About", command=show_info)

# --- Double-click play ---
songs_list.bind("<Double-1>", lambda e: play_song())

# --- Exit handling ---
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
