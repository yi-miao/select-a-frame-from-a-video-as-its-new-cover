import tkinter as tk
from tkinter import filedialog
import vlc
import time
import os
import subprocess

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("800x600")

        # Initialize VLC instance with hardware decoding disabled
        self.instance = vlc.Instance("--no-video-title-show", "--quiet", "--logfile=vlc_log.txt")
        self.player = None
        self.is_paused = False
        self.is_muted = False
        self.jump = 0.01
        self.file_path = None
        self.selected_file = "selected.jpg"

        # Create GUI elements
        self.video_frame = tk.Frame(self.root, bg="grey")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, pady=5)

        # Buttons
        self.select_button = tk.Button(
            self.button_frame, text="Select Video", command=self.select_and_play_video
        )
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.play_pause_button = tk.Button(
            self.button_frame, text="Pause", command=self.toggle_play_pause, state=tk.DISABLED
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        self.seek_backward_button = tk.Button(
            self.button_frame, text=" << ", command=self.seek_backward, state=tk.DISABLED
        )
        self.seek_backward_button.pack(side=tk.LEFT, padx=5)

        self.seek_forward_button = tk.Button(
            self.button_frame, text=" >> ", command=self.seek_forward, state=tk.DISABLED
        )
        self.seek_forward_button.pack(side=tk.LEFT, padx=5)

        self.mute_button = tk.Button(
            self.button_frame, text="Mute", command=self.toggle_mute, state=tk.DISABLED
        )
        self.mute_button.pack(side=tk.LEFT, padx=5)
        
        self.select_button = tk.Button(
            self.button_frame, text="Select", command=self.save_frame, state=tk.DISABLED
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        self.confirm_button = tk.Button(
            self.button_frame, text="Confirm", command=self.confirm_frame, state=tk.DISABLED
        )
        self.confirm_button.pack(side=tk.LEFT, padx=5)

        # Bind window resize event
        self.video_frame.bind("<Configure>", self.resize_video)

        # Bind keyboard controls
        self.root.bind("<space>", lambda event: self.toggle_play_pause())
        self.root.bind("<Left>", lambda event: self.seek_backward())
        self.root.bind("<Right>", lambda event: self.seek_forward())

        self.video_window_id = None

    def select_and_play_video(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")]
        )
        if not self.file_path:
            return

        if self.player:
            self.player.stop()

        self.player = self.instance.media_player_new()
        media = self.instance.media_new(self.file_path)
        self.player.set_media(media)

        if not self.video_window_id:
            self.video_window_id = self.video_frame.winfo_id()

        self.player.set_hwnd(self.video_window_id)

        self.player.play()
        self.is_paused = False
        self.is_muted = True
        self.player.audio_set_mute(True)

        self.play_pause_button.config(text="Pause", state=tk.NORMAL)
        self.seek_backward_button.config(state=tk.NORMAL)
        self.seek_forward_button.config(state=tk.NORMAL)
        self.mute_button.config(text="Sound", state=tk.NORMAL)
        self.seek_forward_button.config(state=tk.NORMAL)
        self.select_button.config(state=tk.NORMAL)
        self.confirm_button.config(state=tk.NORMAL)
        self.update_title_with_progress()
    
    def toggle_play_pause(self):
        if not self.player:
            return
        if self.is_paused:
            self.player.play()
            self.play_pause_button.config(text="Pause")
            self.is_paused = False
        else:
            self.player.pause()
            self.play_pause_button.config(text="Play")
            self.is_paused = True
        
    def seek_backward(self):
        if not self.player:
            return
        current_pos = self.player.get_position()
        self.player.set_position(max(0.0, current_pos - self.jump))  # % jump
        self.update_title_with_progress()
            
    def seek_forward(self):
        if not self.player:
            return
        current_pos = self.player.get_position()
        self.player.set_position(min(1.0, current_pos + self.jump))  # % jump
        self.update_title_with_progress()

    def toggle_mute(self):
        if not self.player:
            return
        self.is_muted = not self.is_muted
        self.player.audio_set_mute(self.is_muted)
        self.mute_button.config(text="Sound" if self.is_muted else "Mute")

    def update_title_with_progress(self):
        if self.player:
            current_time = self.player.get_time()  # ms
            total_time = self.player.get_length()  # ms
            if total_time > 0:
                percent = (current_time / total_time) * 100
                file_name = os.path.basename(self.file_path)
                self.root.title(f"{file_name} - {percent:.1f}% played")
        self.root.after(500, self.update_title_with_progress)  # repeat every 0.5s

    def save_frame(self):
        if self.player:
            # Save snapshot as selected_file in the current directory
            # The second parameter is the file path, the third is width (0 = keep original size)
            result = self.player.video_take_snapshot(0, self.selected_file, 0, 0)
            if result == 0:
                print(f"Frame saved as {self.selected_file}")
            else:
                print("Failed to save frame")
        
    def confirm_frame(self):
        if self.player:
            self.__del__()
            time.sleep(0.1)

        self.output = "output/" + os.path.basename(self.file_path)
        command = [
            "ffmpeg", "-y", "-loglevel", "error", "-i", self.file_path, "-i", self.selected_file,
            "-map", "0", "-map", "1",
            "-c", "copy", "-disposition:v:1", "attached_pic",
            self.output
        ]        
        subprocess.run(command, check=True)
        print(f"Successfully updated cover for {self.file_path} -> {self.output}")

    def resize_video(self, event):
        if self.player:
            self.player.set_hwnd(self.video_frame.winfo_id())

    def __del__(self):
        if self.player:
            self.player.stop()
        self.instance.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
