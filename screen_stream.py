import cv2
import numpy as np
import pyautogui
from threading import Thread

# ===========================
# Screen Stream Settings
# ===========================
SCREEN_STREAM_ENABLED = True
FPS = 15
RESOLUTION = (1280, 720)  # Width x Height

class ScreenStreamer:
    def __init__(self, fps=FPS, resolution=RESOLUTION):
        self.fps = fps
        self.resolution = resolution
        self.running = False
        self.frame = None

    def start_stream(self):
        """Start the screen capture in a separate thread"""
        self.running = True
        Thread(target=self._capture_loop, daemon=True).start()

    def stop_stream(self):
        """Stop the screen capture"""
        self.running = False

    def _capture_loop(self):
        """Continuously capture the screen"""
        while self.running:
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, self.resolution)
            self.frame = frame
            # Limit FPS
            cv2.waitKey(int(1000 / self.fps))

    def get_frame(self):
        """Return the latest frame"""
        return self.frame