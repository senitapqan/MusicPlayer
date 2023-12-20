import pygame
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
import os
import time

class MusicPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Offline Music Player")
        self.master.geometry("1080x720")

        # Initialize variables for keeping track of song position and playback state
        self.pos = 0
        self.stopped = False

        # Set the working directory to the directory containing music files
        self.directory = askdirectory()
        os.chdir(self.directory)
        self.songlist = os.listdir()

        # Create a Tkinter listbox to display the playlist
        self.playlist = tk.Listbox(self.master, font="Helvetica 14 bold", bg="lightgray", selectmode=tk.SINGLE)
        for item in self.songlist:
            self.playlist.insert(tk.END, item)

        # Initialize Pygame and Pygame.mixer for audio playback
        pygame.init()
        pygame.mixer.init()

        # Initialize the index of the currently playing song
        self.current_song_index = 0

        # Create the GUI widgets
        self.create_widgets()

    def create_widgets(self):
        # Song details and controls
        self.var = tk.StringVar()
        self.songtitle = tk.Label(self.master, font="Helvetica 18 bold", textvariable=self.var)

        # Buttons
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 16), padding=10)

        self.play_button = ttk.Button(self.master, text="▶ PLAY", command=self.play, style='TButton')
        self.stop_button = ttk.Button(self.master, text="⏹ STOP", command=self.exit_music_player, style='TButton')
        self.pause_button = ttk.Button(self.master, text="⏸ PAUSE", command=self.pause, style='TButton')
        self.continue_button = ttk.Button(self.master, text="▶ CONTINUE", command=self.unpause, style='TButton')
        self.prev_button = ttk.Button(self.master, text="⏮ PREV", command=self.prev_song, style='TButton')
        self.next_button = ttk.Button(self.master, text="⏭ NEXT", command=self.next_song, style='TButton')

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.master, orient=tk.HORIZONTAL, length=800, mode='determinate')

        # Time selection
        self.time_scale = tk.Scale(self.master, from_=0, to=100, orient=tk.HORIZONTAL, label="Jump to Time (%)", length=800, showvalue=False, command=self.jump_to_time)
        self.time_scale.set(0)

        # Pack widgets using grid layout
        self.songtitle.grid(row=0, column=0, columnspan=6, pady=20)
        self.playlist.grid(row=1, column=0, columnspan=6, padx=20, pady=20, sticky=tk.W+tk.E)
        self.play_button.grid(row=2, column=0, padx=20, pady=20)
        self.stop_button.grid(row=2, column=1, padx=20, pady=20)
        self.pause_button.grid(row=2, column=2, padx=20, pady=20)
        self.continue_button.grid(row=2, column=3, padx=20, pady=20)
        self.prev_button.grid(row=3, column=0, padx=20, pady=20)
        self.next_button.grid(row=3, column=1, padx=20, pady=20)
        self.progress_bar.grid(row=4, column=0, columnspan=6, pady=20)
        self.time_scale.grid(row=5, column=0, columnspan=6, pady=20)

    def play(self):
        # Reset the position and set the currently selected song
        self.pos = 0
        self.current_song_index = self.playlist.curselection()[0]
        pygame.mixer.music.load(self.playlist.get(self.current_song_index))
        self.var.set(self.playlist.get(self.current_song_index))
        pygame.mixer.music.play()
        self.update_duration()

    def next_song(self):
        # Move to the next song in the playlist
        self.current_song_index = (self.current_song_index + 1) % len(self.songlist)
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(self.current_song_index)
        self.play()

    def prev_song(self):
        # Move to the previous song in the playlist
        self.current_song_index = (self.current_song_index - 1) % len(self.songlist)
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(self.current_song_index)
        self.play()

    def update_duration(self):
        # Update the progress bar and song details during playback
        duration = pygame.mixer.Sound(self.playlist.get(self.current_song_index)).get_length()
        while pygame.mixer.music.get_busy():
            current_pos = pygame.mixer.music.get_pos() + self.pos
            current_pos_sec = current_pos / 1000.0

            # Calculate the progress percentage for the progress bar
            progress_percentage = (current_pos / (duration * 1000)) * 100

            # Update the progress bar, song details, and refresh the GUI
            self.progress_bar['value'] = progress_percentage
            self.var.set(f"{self.playlist.get(self.current_song_index)} - {int(current_pos_sec)}s")
            self.master.update()

            # Pause for 1 second to avoid rapid updates and improve performance
            time.sleep(1)

        # If the stop flag is not set, move to the next song in the playlist
        if self.stopped is False:
            self.next_song()

    def exit_music_player(self):
        # Set the stop flag and stop the music playback
        self.stopped = True
        pygame.mixer.music.stop()

    def pause(self):
        # Set the stop flag and pause the music playback
        self.stopped = True
        pygame.mixer.music.pause()

    def unpause(self):
        # Unpause the music playback and update the duration
        pygame.mixer.music.unpause()
        self.stopped = False
        self.update_duration()

    def jump_to_time(self, scale_value):
        # Jump to a specific time in the currently playing song
        duration = pygame.mixer.Sound(self.playlist.get(self.current_song_index)).get_length()
        jump_time = (float(scale_value) / 100) * duration

        # Set the position to jump to and rewind the music
        self.pos = int(jump_time * 1000)
        pygame.mixer.music.rewind()
        pygame.mixer.music.play(start=int(jump_time))


if __name__ == "__main__":
    # Create the Tkinter root window and the MusicPlayer instance
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()

