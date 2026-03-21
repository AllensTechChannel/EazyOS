#!/usr/bin/env python3
"""
Modern Media Player
A sleek audio player built with tkinter and pygame.mixer
"""

import tkinter as tk
from tkinter import filedialog, ttk
import pygame.mixer as mixer
import os
from pathlib import Path
import time
import threading

class ModernMediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Player")
        self.root.geometry("480x520")
        self.root.configure(bg="#c0c0c0")
        self.root.resizable(False, False)
        
        # Initialize mixer
        mixer.init()
        
        # Player state
        self.playlist = []
        self.current_track = None
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.song_length = 0
        self.update_thread = None
        self.should_update = False
        
        # UI Setup
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview (playlist) - Windows 95 style
        style.configure("Playlist.Treeview",
                       background="#ffffff",
                       foreground="#000000",
                       fieldbackground="#ffffff",
                       borderwidth=2,
                       relief="sunken",
                       font=('MS Sans Serif', 8))
        style.map('Playlist.Treeview',
                 background=[('selected', '#000080')],
                 foreground=[('selected', '#ffffff')])
        
        # Configure Scrollbar - Windows 95 style
        style.configure("Playlist.Vertical.TScrollbar",
                       background="#c0c0c0",
                       troughcolor="#ffffff",
                       borderwidth=1,
                       arrowsize=16)
        
        # Configure Scale/Slider
        style.configure("Win95.Horizontal.TScale",
                       background="#c0c0c0",
                       troughcolor="#ffffff",
                       borderwidth=1)
        
    def setup_ui(self):
        """Create the user interface"""
        # Windows 95 style colors
        win95_bg = "#c0c0c0"
        win95_dark = "#808080"
        win95_light = "#ffffff"
        win95_text = "#000000"
        win95_highlight = "#000080"
        
        # Title Bar style frame
        title_frame = tk.Frame(self.root, bg=win95_highlight, height=25)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="Media Player",
                              font=('MS Sans Serif', 8, 'bold'),
                              bg=win95_highlight,
                              fg=win95_light,
                              anchor='w')
        title_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Main container with sunken border
        main_container = tk.Frame(self.root, bg=win95_bg, relief="flat")
        main_container.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Display Frame (sunken)
        display_outer = tk.Frame(main_container, bg=win95_dark, relief="sunken", bd=2)
        display_outer.pack(fill=tk.X, padx=8, pady=8)
        
        display_frame = tk.Frame(display_outer, bg="#000000", height=60)
        display_frame.pack(fill=tk.BOTH, padx=1, pady=1)
        display_frame.pack_propagate(False)
        
        # LED-style display
        self.track_label = tk.Label(display_frame,
                                   text="No track loaded",
                                   font=('Courier New', 10, 'bold'),
                                   bg="#000000",
                                   fg="#00ff00",
                                   anchor='w')
        self.track_label.pack(fill=tk.X, padx=5, pady=3)
        
        self.artist_label = tk.Label(display_frame,
                                    text="Ready",
                                    font=('Courier New', 8),
                                    bg="#000000",
                                    fg="#00ff00",
                                    anchor='w')
        self.artist_label.pack(fill=tk.X, padx=5)
        
        # Time display frame
        time_outer = tk.Frame(main_container, bg=win95_dark, relief="sunken", bd=2)
        time_outer.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        time_display = tk.Frame(time_outer, bg="#000000")
        time_display.pack(fill=tk.X, padx=1, pady=1)
        
        time_inner = tk.Frame(time_display, bg="#000000")
        time_inner.pack(fill=tk.X, padx=5, pady=3)
        
        self.current_time_label = tk.Label(time_inner,
                                          text="00:00",
                                          font=('Courier New', 10, 'bold'),
                                          bg="#000000",
                                          fg="#ff0000")
        self.current_time_label.pack(side=tk.LEFT)
        
        tk.Label(time_inner,
                text=" / ",
                font=('Courier New', 10),
                bg="#000000",
                fg="#808080").pack(side=tk.LEFT)
        
        self.total_time_label = tk.Label(time_inner,
                                        text="00:00",
                                        font=('Courier New', 10, 'bold'),
                                        bg="#000000",
                                        fg="#ff0000")
        self.total_time_label.pack(side=tk.LEFT)
        
        # Progress bar frame
        progress_outer = tk.Frame(main_container, bg=win95_dark, relief="sunken", bd=1)
        progress_outer.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(progress_outer,
                                     from_=0,
                                     to=100,
                                     orient=tk.HORIZONTAL,
                                     variable=self.progress_var,
                                     style="Win95.Horizontal.TScale",
                                     command=self.seek)
        self.progress_bar.pack(fill=tk.X, padx=2, pady=2)
        
        # Control Buttons Frame with raised relief
        controls_outer = tk.Frame(main_container, bg=win95_bg)
        controls_outer.pack(pady=(0, 8))
        
        controls_frame = tk.Frame(controls_outer, bg=win95_bg)
        controls_frame.pack()
        
        # Button style - Windows 95 raised buttons
        btn_config = {
            'font': ('MS Sans Serif', 8, 'bold'),
            'bg': win95_bg,
            'fg': win95_text,
            'activebackground': win95_bg,
            'activeforeground': win95_text,
            'relief': 'raised',
            'bd': 2,
            'width': 8,
            'height': 2,
            'cursor': 'hand2'
        }
        
        # Previous button
        self.prev_btn = tk.Button(controls_frame,
                                 text="<< Prev",
                                 command=self.previous_track,
                                 **btn_config)
        self.prev_btn.pack(side=tk.LEFT, padx=3)
        
        # Play/Pause button
        self.play_btn = tk.Button(controls_frame,
                                 text="Play",
                                 command=self.play_pause,
                                 **btn_config)
        self.play_btn.pack(side=tk.LEFT, padx=3)
        
        # Stop button
        self.stop_btn = tk.Button(controls_frame,
                                text="Stop",
                                command=self.stop,
                                **btn_config)
        self.stop_btn.pack(side=tk.LEFT, padx=3)
        
        # Next button
        self.next_btn = tk.Button(controls_frame,
                                 text="Next >>",
                                 command=self.next_track,
                                 **btn_config)
        self.next_btn.pack(side=tk.LEFT, padx=3)
        
        # Volume Frame
        volume_group = tk.LabelFrame(main_container,
                                    text="Volume",
                                    font=('MS Sans Serif', 8),
                                    bg=win95_bg,
                                    fg=win95_text,
                                    relief="groove",
                                    bd=2)
        volume_group.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        volume_inner = tk.Frame(volume_group, bg=win95_bg)
        volume_inner.pack(fill=tk.X, padx=5, pady=5)
        
        self.volume_var = tk.DoubleVar(value=70)
        volume_slider = ttk.Scale(volume_inner,
                                 from_=0,
                                 to=100,
                                 orient=tk.HORIZONTAL,
                                 variable=self.volume_var,
                                 style="Win95.Horizontal.TScale",
                                 command=self.change_volume)
        volume_slider.pack(fill=tk.X)
        
        # Playlist Frame
        playlist_group = tk.LabelFrame(main_container,
                                      text="Playlist",
                                      font=('MS Sans Serif', 8),
                                      bg=win95_bg,
                                      fg=win95_text,
                                      relief="groove",
                                      bd=2)
        playlist_group.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        playlist_container = tk.Frame(playlist_group, bg=win95_bg)
        playlist_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(playlist_container, style="Playlist.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Playlist treeview
        self.playlist_view = ttk.Treeview(playlist_container,
                                         columns=('track',),
                                         show='tree',
                                         selectmode='browse',
                                         yscrollcommand=scrollbar.set,
                                         style="Playlist.Treeview",
                                         height=6)
        self.playlist_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_view.yview)
        
        self.playlist_view.bind('<Double-Button-1>', self.on_track_select)
        self.playlist_view.bind('<Delete>', self.delete_track)
        self.playlist_view.bind('<BackSpace>', self.delete_track)
        
        # Button frame
        button_frame = tk.Frame(main_container, bg=win95_bg)
        button_frame.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        # Add Files Button
        add_btn = tk.Button(button_frame,
                          text="Add Files...",
                          command=self.add_files,
                          font=('MS Sans Serif', 8),
                          bg=win95_bg,
                          fg=win95_text,
                          relief='raised',
                          bd=2,
                          width=12,
                          cursor='hand2')
        add_btn.pack(side=tk.LEFT, padx=2)
        
        # Remove Files Button
        remove_btn = tk.Button(button_frame,
                             text="Remove",
                             command=lambda: self.delete_track(),
                             font=('MS Sans Serif', 8),
                             bg=win95_bg,
                             fg=win95_text,
                             relief='raised',
                             bd=2,
                             width=12,
                             cursor='hand2')
        remove_btn.pack(side=tk.LEFT, padx=2)
        
    def add_files(self):
        """Add audio files to playlist"""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg *.flac"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ]
        )
        
        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
                filename = os.path.basename(file)
                self.playlist_view.insert('', 'end', text=filename, values=(file,))
        
    def on_track_select(self, event):
        """Handle track selection from playlist"""
        selection = self.playlist_view.selection()
        if selection:
            item = self.playlist_view.item(selection[0])
            track_path = item['values'][0]
            self.current_index = self.playlist.index(track_path)
            self.load_track(track_path)
            self.play()
    
    def delete_track(self, event=None):
        """Delete selected track from playlist"""
        selection = self.playlist_view.selection()
        if selection:
            item = self.playlist_view.item(selection[0])
            track_path = item['values'][0]
            
            # If deleting the currently playing track, stop it
            if track_path == self.current_track:
                self.stop()
                self.current_track = None
                self.track_label.config(text="No track loaded")
                self.artist_label.config(text="Select a track to begin")
            
            # Remove from playlist and treeview
            if track_path in self.playlist:
                index = self.playlist.index(track_path)
                self.playlist.remove(track_path)
                self.playlist_view.delete(selection[0])
                
                # Update current_index if needed
                if self.current_index > index:
                    self.current_index -= 1
                elif self.current_index == index:
                    self.current_index = -1
            
    def load_track(self, track_path):
        """Load a track for playback"""
        try:
            mixer.music.load(track_path)
            self.current_track = track_path
            filename = os.path.basename(track_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            self.track_label.config(text=name_without_ext)
            self.artist_label.config(text="Playing...")
            
            # Get song length (approximate)
            sound = mixer.Sound(track_path) if track_path.endswith('.wav') else None
            if sound:
                self.song_length = sound.get_length()
            else:
                self.song_length = 0  # For MP3, we can't easily get length without additional libraries
                
            self.total_time_label.config(text=self.format_time(self.song_length))
            
        except Exception as e:
            print(f"Error loading track: {e}")
            self.track_label.config(text="Error loading track")
            
    def play(self):
        """Play the current track"""
        if self.current_track:
            mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.play_btn.config(text="Pause")
            self.start_position_update()
            
    def pause(self):
        """Pause playback"""
        mixer.music.pause()
        self.is_paused = True
        self.play_btn.config(text="Play")
        self.should_update = False
        
    def unpause(self):
        """Resume playback"""
        mixer.music.unpause()
        self.is_paused = False
        self.play_btn.config(text="Pause")
        self.start_position_update()
        
    def play_pause(self):
        """Toggle play/pause"""
        if not self.current_track and self.playlist:
            self.current_index = 0
            self.load_track(self.playlist[0])
            self.play()
        elif self.is_paused:
            self.unpause()
        elif self.is_playing:
            self.pause()
        else:
            self.play()
            
    def stop(self):
        """Stop playback"""
        mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.play_btn.config(text="Play")
        self.should_update = False
        self.progress_var.set(0)
        self.current_time_label.config(text="00:00")
        
    def next_track(self):
        """Play next track in playlist"""
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.load_track(self.playlist[self.current_index])
            self.play()
            
    def previous_track(self):
        """Play previous track in playlist"""
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self.load_track(self.playlist[self.current_index])
            self.play()
            
    def change_volume(self, val):
        """Adjust volume"""
        volume = float(val) / 100
        mixer.music.set_volume(volume)
        
    def seek(self, val):
        """Seek to position (limited support in pygame.mixer)"""
        # Note: pygame.mixer has limited seeking support
        # This is a placeholder for better libraries
        pass
        
    def start_position_update(self):
        """Start updating the position indicator"""
        self.should_update = True
        if not self.update_thread or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_position, daemon=True)
            self.update_thread.start()
            
    def update_position(self):
        """Update progress bar and time (runs in thread)"""
        start_time = time.time()
        while self.should_update and self.is_playing:
            if mixer.music.get_busy() and not self.is_paused:
                elapsed = time.time() - start_time
                if self.song_length > 0:
                    progress = (elapsed / self.song_length) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(min(p, 100)))
                self.root.after(0, lambda e=elapsed: self.current_time_label.config(text=self.format_time(e)))
                time.sleep(0.1)
            else:
                # Song ended
                if not self.is_paused:
                    self.root.after(0, self.next_track)
                break
                
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
        
    def on_closing(self):
        """Clean up on exit"""
        self.should_update = False
        mixer.music.stop()
        mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ModernMediaPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()