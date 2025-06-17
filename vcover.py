import cv2
import os
import time
import ffmpeg
import subprocess

class CoverSelector:
    def __init__(self, video_path, output_file, cover_file="selected.jpg"):
        self.video = video_path
        self.output = output_file
        self.cover = cover_file
            
    def set_mp4_cover(self):
        command = [
            "ffmpeg", "-loglevel", "error", "-i", self.video, "-i", self.cover,
            "-map", "0", "-map", "1",
            "-c", "copy", "-disposition:v:1", "attached_pic",
            self.output
        ]
        subprocess.run(command, check=True)
        print(f"Successfully updated cover for {self.video} -> {self.output}")
        
    def run(self, num_frames = 20, beta = 5):
        window_name = "Select Cover"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  
        cv2.resizeWindow(window_name, 500, 400)
        self.cap = cv2.VideoCapture(self.video)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_index = 0
        while True:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = self.cap.read()
            if frame is None:
                self.cleanup()
                break
            percent = (frame_index / frame_count) * 100
            title_text = "Frame " + str(frame_index) + " - " + str(round(percent, 1)) + " %" 
            cv2.setWindowTitle(window_name, title_text)
            cv2.imshow(window_name, frame)
            key = cv2.waitKeyEx(1)
            if key == ord('q'):     # quit
                self.cleanup()
                exit()
            elif key == ord('s'):   # select the frame as cover, can be multiple times
                cv2.imwrite(self.cover, frame)
                print(f"Cover image saved as {self.cover}")
            elif key == ord('c'):   # confirm the selection
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.cleanup()
                time.sleep(0.1)
                self.set_mp4_cover()
                # print(f"{self.video} cover replaced with {self.cover}")
                exit()
            elif key == 2424832:  # Left arrow
                frame_index = max(frame_index - num_frames, 0)
            elif key == 2555904:  # Right arrow
                frame_index = min(frame_index + num_frames, frame_count - 1)
            elif key == 2490368:  # Up arrow
                frame_index = max(frame_index - num_frames//beta, 0)
            elif key == 2621440:  # Down arrow
                frame_index = min(frame_index + num_frames//beta, frame_count - 1)

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":  
    # usesage: python vcover.py -v "video_in.mp4" -o "video_out.mp4"
    import argparse

    parser = argparse.ArgumentParser(description="Process video and cover file.")
    parser.add_argument("-v", "--video", required=True, help="Path to video file")
    parser.add_argument("-o", "--output", required=True, help="Path to output file")
    args = parser.parse_args()
  
    app = CoverSelector(args.video, args.output)
    app.run(60)
