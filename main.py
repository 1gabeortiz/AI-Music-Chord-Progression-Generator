import tkinter as tk
from tkinter import ttk
from music21 import *
import random
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageTk
import threading
import vlc
import atexit
import pygame
import time
import os
from pydub import AudioSegment
from pydub.playback import play


# Pygame setup
pygame.init()

# Initialize an empty dictionary to store the sounds by note and octave
note_files = {}

# Path to the folder containing all WAV files
folder_path = r"C:\Users\Gabe\Desktop\AIChordProgressionGenerator\notes"

# Load note files based on your naming convention
note_files = {}

def load_note_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            # Parse the filename for note and octave
            parts = filename.split('-')
            note_letter = parts[0].upper()  # Get the note letter (e.g., "D")
            is_sharp = len(parts) > 1  # Check if it’s a sharp note
            octave = parts[-1].replace(".wav", "")  # Get the octave number
            
            # Construct the note key
            note = note_letter + ('#' if is_sharp else '') + octave
            note_files[note] = AudioSegment.from_file(os.path.join(directory, filename))

# Call this function to load files from your WAV directory
load_note_files(r"C:\Users\Gabe\Desktop\AIChordProgressionGenerator\notes")

# Function to play chords by layering note sounds
def play_chord(notes):
    if not notes:
        return  # No notes to play
    
    chord_sound = None
    
    for note in notes:
        if note in note_files:
            if chord_sound is None:
                chord_sound = note_files[note]
            else:
                chord_sound = chord_sound.overlay(note_files[note])
    
    if chord_sound:
        play(chord_sound)

# VLC setup
video_instance = vlc.Instance()
player = video_instance.media_player_new()

# Load the media file
media = video_instance.media_new(r"C:\Users\Gabe\Desktop\AIChordProgressionGenerator\AI Music Chord Progression Generator TUTORIAL.mp4")
player.set_media(media)

# Cleanup function to stop playback and release resources on exit
def cleanup():
    if player.is_playing():
        player.stop()
    video_instance.release()

atexit.register(cleanup)
# Function to generate chord progression based on key, genre, and mood
def generate_progression():
    global generated_chords

    selected_key = key_var.get()
    mode = mode_var.get()
    genre = genre_var.get()
    mood = mood_var.get()
    

    if mode == 'Major':
        tonic = key.Key(selected_key, 'major')
    else:
        tonic = key.Key(selected_key, 'minor')

    genre_mood_progressions = {
        "Jazz": {
            "Smooth": [['ii7', 'V7', 'Imaj7', 'vi7'], ['Imaj7', 'IVmaj7', 'ii7']],
            "Energetic": [['V7', 'Imaj7', 'ii7', 'vi7'], ['ii7', 'V7', 'iii7', 'vi7']]
        },
        "Classical": {
            "Dramatic": [['i', 'iv', 'V7', 'i'], ['i', 'VI', 'iv', 'V']],
            "Peaceful": [['I', 'IV', 'V', 'I'], ['i', 'iv', 'V', 'i']]
        },
        "Rap": {
            "Energetic": [['i', 'bVII', 'bVI', 'V'], ['i', 'iv', 'V', 'bVII'], ['i', 'bIII', 'bVII', 'V']],
            "Chill": [['i', 'iv', 'v', 'VII'], ['i', 'VI', 'bVII', 'v'], ['i', 'V', 'VI', 'IV']],
            "Dark": [['i', 'v', 'bVII', 'iv'], ['i', 'bVI', 'iv', 'bIII'], ['i', 'bIII', 'iv', 'bVII']],
            "Uplifting": [['i', 'III', 'iv', 'V'], ['i', 'VI', 'V', 'iv'], ['i', 'VII', 'iv', 'V']]
        },
        "Pop": {
            "Energetic": [['I', 'V', 'vi', 'IV'], ['I', 'IV', 'V', 'IV'], ['vi', 'IV', 'I', 'V']],
            "Chill": [['I', 'V', 'vi'], ['I', 'IV', 'vi', 'V'], ['vi', 'IV', 'I', 'V']],
            "Uplifting": [['I', 'vi', 'IV', 'V'], ['I', 'IV', 'vi', 'iii'], ['IV', 'I', 'V', 'vi']],
            "Dramatic": [['vi', 'IV', 'I', 'V'], ['IV', 'I', 'V', 'vi'], ['I', 'IV', 'ii', 'V']],
            "Mellow": [['I', 'IV', 'V', 'vi'], ['ii', 'V', 'I'], ['vi', 'IV', 'I']]
        },
        "Rock": {
            "Energetic": [['I', 'IV', 'V', 'I'], ['I', 'vi', 'IV', 'V']],
            "Mellow": [['vi', 'IV', 'I', 'V'], ['IV', 'I', 'V', 'vi']]
        }
    }

    genre_fallback_progressions = {
        "Jazz": [['ii7', 'V7', 'Imaj7'], ['Imaj7', 'IVmaj7', 'ii7']],
        "Classical": [['I', 'IV', 'V', 'I'], ['i', 'iv', 'V', 'i']],
        "Rap": [['i', 'bVII', 'bVI', 'V'], ['i', 'IV', 'v']],
        "Pop": [['I', 'IV', 'V', 'I'], ['I', 'V', 'vi']],
        "Rock": [['I', 'IV', 'V', 'I'], ['I', 'vi', 'IV']]
    }

    default_progressions = [['I', 'IV', 'V', 'I']]

    used_fallback = False

    if genre in genre_mood_progressions and mood in genre_mood_progressions[genre]:
        progressions = genre_mood_progressions[genre][mood]
    elif genre in genre_fallback_progressions:
        progressions = genre_fallback_progressions[genre]
        used_fallback = True
    else:
        progressions = default_progressions
        used_fallback = True

    progression = random.choice(progressions)

    generated_chords = []

    for rn in progression:
        chord_obj = roman.RomanNumeral(rn, tonic)
        chord_name = chord_obj.root().name
        if chord_obj.quality == "major":
            chord_name += "maj" if not chord_obj.isSeventh() else "7"
        elif chord_obj.quality == "minor":
            chord_name += "min" if not chord_obj.isSeventh() else "min7"
        elif chord_obj.quality == "diminished":
            chord_name += "dim" if not chord_obj.isSeventh() else "dim7"
        elif chord_obj.quality == "augmented":
            chord_name += "aug"
        else:
            chord_name += chord_obj.quality
        generated_chords.append(chord_name)

    toggle_progression_view()

    if used_fallback:
        result_label.config(text=result_label.cget("text") + "\n(Note: Fallback progression used for genre.)")

def toggle_progression_view():
    result_label.config(text="Chord Progression: " + ' - '.join(generated_chords))

def reset():
    key_var.set('C')
    mode_var.set('Major')
    genre_var.set('Rap')
    mood_var.set('Energetic')
    result_label.config(text="")
    stop_video()

def exit_program():
    stop_video()
    root.quit()
    root.destroy()

# Function to play video
def play_video():
    if not player.is_playing():
        player.play()

# Function to pause or resume the video
def pause_video():
    if player.is_playing():
        player.pause()  # This will toggle pause and resume

# Function to stop the video
def stop_video():
    if player.is_playing():
        player.stop()  # Stops playback completely

# Root setup
root = tk.Tk()
root.title("AI Music Chord Progression Generator")
root.geometry("900x700")
root.configure(bg="black")

# Style setup
style = ttk.Style()
style.theme_use("default")
style.configure("TFrame", background="black")
style.configure("TLabel", background="black", foreground="white", font=("Helvetica", 12))
style.configure("TButton", background="black", foreground="white")
style.configure("TCombobox", fieldbackground="black", background="black", foreground="white")

# Canvas and Scrollable Frame setup
canvas = tk.Canvas(root, bg="black", highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)

# Frame inside canvas
scrollable_frame = ttk.Frame(canvas, style="TFrame")
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

def update_scroll_region(event):
    """Updates the scroll region and centers the content inside the canvas."""
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas_width = canvas.winfo_width()
    frame_width = scrollable_frame.winfo_width()
    x_offset = max((canvas_width - frame_width) // 2, 0)  # Center horizontally
    canvas.coords(canvas_window, x_offset, 0)  # Update window coordinates

scrollable_frame.bind("<Configure>", update_scroll_region)

# Pack canvas and scrollbar
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.config(yscrollcommand=scrollbar.set)

# Content inside scrollable frame
content_frame = ttk.Frame(scrollable_frame, style="TFrame")
content_frame.grid(row=0, column=0, padx=20, pady=20)

# Content Widgets
logo = Image.open("logo.png").resize((40, 100), Image.Resampling.LANCZOS)
logo_tk = ImageTk.PhotoImage(logo)
logo_label = tk.Label(content_frame, image=logo_tk, bg="black")
logo_label.grid(row=0, column=0, pady=10)

header = ttk.Label(content_frame, text="AI Music Chord Progression Generator", style="TLabel")
header.grid(row=1, column=0, pady=10)

selection_frame = ttk.Frame(content_frame, style="TFrame")
selection_frame.grid(row=2, column=0, pady=10)

key_var = tk.StringVar(value='C')
ttk.Label(selection_frame, text="Select Key:", style="TLabel").grid(row=0, column=0, padx=10, pady=5)
ttk.Combobox(selection_frame, textvariable=key_var, values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]).grid(row=0, column=1, padx=10, pady=5)

mode_var = tk.StringVar(value='Major')
ttk.Label(selection_frame, text="Select Mode:", style="TLabel").grid(row=1, column=0, padx=10, pady=5)
ttk.Combobox(selection_frame, textvariable=mode_var, values=["Major", "Minor"]).grid(row=1, column=1, padx=10, pady=5)

genre_var = tk.StringVar(value='Rap')
ttk.Label(selection_frame, text="Select Genre:", style="TLabel").grid(row=2, column=0, padx=10, pady=5)
ttk.Combobox(selection_frame, textvariable=genre_var, values=["Jazz", "Classical", "Rap", "Pop", "Rock"]).grid(row=2, column=1, padx=10, pady=5)

mood_var = tk.StringVar(value='Energetic')
ttk.Label(selection_frame, text="Select Mood:", style="TLabel").grid(row=3, column=0, padx=10, pady=5)
ttk.Combobox(selection_frame, textvariable=mood_var, values=["Smooth", "Energetic", "Dramatic", "Peaceful", "Chill", "Dark", "Uplifting"]).grid(row=3, column=1, padx=10, pady=5)

ttk.Button(selection_frame, text="Generate Chord Progression", command=generate_progression).grid(row=4, columnspan=2, pady=10)
ttk.Button(selection_frame, text="Reset", command=reset).grid(row=5, columnspan=2, pady=5)
ttk.Button(selection_frame, text="Exit", command=exit_program).grid(row=6, columnspan=2, pady=5)

result_label = ttk.Label(content_frame, text="", style="TLabel")
result_label.grid(row=3, column=0, pady=10)

video_frame = ttk.Frame(content_frame, style="TFrame")
video_frame.grid(row=4, column=0, pady=10)
video_label = tk.Label(video_frame, bg="black")
video_label.pack()

ttk.Button(video_frame, text="Play Tutorial", command=play_video).pack(side=tk.LEFT, padx=10)
ttk.Button(video_frame, text="Pause Video", command=pause_video).pack(side=tk.LEFT, padx=10)
ttk.Button(video_frame, text="Stop Video", command=stop_video).pack(side=tk.LEFT, padx=10)

# Mouse scroll function
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind_all("<MouseWheel>", on_mouse_wheel)

root.mainloop()