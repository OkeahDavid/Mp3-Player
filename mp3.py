import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pygame
import os
from ttkthemes import themed_tk as tkth


# Initialize pygame
pygame.init()

# Create the player class
class MP3Player:
    def __init__(self):
        self.playlist = []
        self.current_index = 0
        self.volume = 0.5
        self.paused = False
        self.current_song_duration = 0  # Store the duration of the currently playing song
        self.current_sound = None

    def load_playlist(self, directory):
        self.playlist = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith('.mp3')]
        self.current_index = 0

    def play(self):
        pygame.mixer.music.load(self.playlist[self.current_index])
        self.current_song_duration = pygame.mixer.Sound(self.playlist[self.current_index]).get_length()
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()

    def pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def stop(self):
        pygame.mixer.music.stop()

    def next_song(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_song(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def set_volume(self, volume):
        self.volume = volume
        pygame.mixer.music.set_volume(self.volume)

# Create the player instance
player = MP3Player()

# Create a MediaControlsApp class
class MediaControlsApp:
    def __init__(self, root):
        self.root = root
        self.media_controls_frame = ttk.Frame(root)
        self.media_controls_frame.pack()

        # Create style
        self.style = ttk.Style()
        self.style.configure("Media.TButton", padding=6, relief="flat", font=("Helvetica", 12))
        self.style.configure("Progress.Horizontal.TScale", sliderlength=20, sliderthickness=15)

        # Create buttons
        self.play_button = ttk.Button(self.media_controls_frame, text="Play", command=play_button_clicked, style="Media.TButton")
        self.pause_button = ttk.Button(self.media_controls_frame, text="Pause", command=pause_button_clicked, style="Media.TButton")
        self.stop_button = ttk.Button(self.media_controls_frame, text="Stop", command=stop_button_clicked, style="Media.TButton")
        self.previous_button = ttk.Button(self.media_controls_frame, text="Previous", command=previous_button_clicked, style="Media.TButton")
        self.next_button = ttk.Button(self.media_controls_frame, text="Next", command=next_button_clicked, style="Media.TButton")

        # Create progress bar
        self.progress_bar = ttk.Scale(self.media_controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, style="Progress.Horizontal.TScale", command=volume_slider_changed)

        # Create labels for progress and duration
        self.progress_label = ttk.Label(self.media_controls_frame, text="Progress: 00:00")
        self.duration_label = ttk.Label(self.media_controls_frame, text="Duration: 00:00")

        # Pack buttons, progress bar, and labels
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.previous_button.pack(side=tk.LEFT, padx=5)
        self.next_button.pack(side=tk.LEFT, padx=5)
        self.progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.progress_label.pack(side=tk.LEFT, padx=5)  # Display progress label before duration label
        self.duration_label.pack(side=tk.LEFT, padx=5)

        # Create a slider for seeking
        self.seek_slider = ttk.Scale(self.media_controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, style="Progress.Horizontal.TScale", command=self.seek_slider_changed)
        self.seek_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    def seek_slider_changed(self, value):
        position = float(value) / 100 * player.current_song_duration
        pygame.mixer.music.set_pos(position)
        self.update_progress_label(position)

    def update_progress_label(self, progress):
        minutes, seconds = divmod(int(progress), 60)
        formatted_time = f"{minutes:02}:{seconds:02}"
        self.progress_label.config(text=f"Progress: {formatted_time}")

    def update_duration_label(self, duration):
        minutes, seconds = divmod(int(duration), 60)
        formatted_time = f"{minutes:02}:{seconds:02}"
        self.duration_label.config(text=f"Duration: {formatted_time}")
    
    def update_progress(self):
        if pygame.mixer.music.get_busy():
            position = pygame.mixer.music.get_pos() / 1000  # Get position in seconds
            self.update_progress_label(position)
            self.seek_slider.set(position)  # Update the seek slider value
        self.root.after(1000, self.update_progress)


# GUI setup
def play_button_clicked():
    if not pygame.mixer.music.get_busy():
        player.play()
        media_controls_app.update_duration_label(player.current_song_duration)
        media_controls_app.seek_slider.set(0)  # Set seek slider value to 0

def update_seek_slider():
    if pygame.mixer.music.get_busy():
        position = pygame.mixer.music.get_pos() / 1000  # Get position in seconds
        media_controls_app.update_progress_label(position)
        media_controls_app.seek_slider.set(position)  # Update the seek slider value
        media_controls_app.root.after(1000, update_seek_slider)  # Update every second




def pause_button_clicked():
    player.pause()

def stop_button_clicked():
    player.stop()

def next_button_clicked():
    player.next_song()

def previous_button_clicked():
    player.previous_song()

def volume_slider_changed(value):
    player.set_volume(float(value) / 100)

def load_playlist_button_clicked():
    playlist_directory = filedialog.askdirectory(title="Select Directory with MP3 Files")
    if playlist_directory:
        player.load_playlist(playlist_directory)
        update_playlist()

def update_playlist():
    playlist_box.delete(0, tk.END)
    for song in player.playlist:
        playlist_box.insert(tk.END, os.path.basename(song))

root = tkth.ThemedTk(theme="arc")
root.title("Simple MP3 Player")

# Create GUI elements
load_playlist_button = tk.Button(root, text="Load Playlist", command=load_playlist_button_clicked)
playlist_box = tk.Listbox(root)

# Create the media controls app
media_controls_app = MediaControlsApp(root)

# Pack layout for GUI elements
load_playlist_button.pack(padx=10, pady=10, fill=tk.X)
playlist_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Start the GUI main loop
root.after(1000, update_seek_slider)  # Start updating seek slider every second
root.mainloop()
