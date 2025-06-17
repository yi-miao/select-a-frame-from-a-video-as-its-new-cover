import cv2
import os
import time
from mutagen.mp4 import MP4, MP4Cover

class CoverSelector:
    def __init__(self, video_path, cover_file):
        self.video = video_path
        self.cover = cover_file

    def set_mp4_cover(self, video_path, cover_path):
        try:
            video = MP4(video_path)
            with open(cover_path, 'rb') as f:
                cover_data = f.read()
                
            # Create MP4Cover object with the image data
            cover = MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)        
            # Set the cover art in the MP4 metadata
            video['covr'] = [cover]
            
            # Save the changes
            video.save()
            print(f"Successfully set cover for {video_path}")
        except Exception as e:
            print(f"Error: {e}")
        
    def run(self, num_frames = 20, beta = 5):
        window_name = "Select Cover"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  
        cv2.resizeWindow(window_name, 500, 400)
        self.cap = cv2.VideoCapture(self.video)
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_index = 0
        print(f"Controls: Space = Pause/Resume, ← back {num_frames} frames, → forward {num_frames} frames, 's' select, 'q' quit")
        while True:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = self.cap.read()
            if frame is None:
                print("End of video or invalid frame.")
                break
            percent = (frame_index / frame_count) * 100
            footer_text = "Frame " + str(frame_index) + " - " + str(round(percent, 1)) + " %" 
            cv2.setWindowTitle(window_name, footer_text)
            cv2.imshow(window_name, frame)
            key = cv2.waitKeyEx(0)
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
                self.set_mp4_cover(self.video, self.cover)
                print(f"{self.video} cover replaced with {self.cover}")
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
    # usesage: python vcover.py -v "test.mp4" -c selected.jpg
    import argparse

    parser = argparse.ArgumentParser(description="Process video and cover file.")
    parser.add_argument("-v", "--video", required=True, help="Path to video file")
    parser.add_argument("-c", "--cover", required=True, help="Path to cover file")
    # Display results

    args = parser.parse_args()
    print(f"Video file selected: {args.video}")
    print(f"Cover file selected: {args.cover}")
    
    vcs = CoverSelector(args.video, args.cover)
    vcs.run(60)
