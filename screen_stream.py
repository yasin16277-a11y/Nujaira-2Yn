import time
import logging
from threading import Thread

logger = logging.getLogger(__name__)

# ===========================
# Screen Stream Settings
# ===========================
FPS = 15
RESOLUTION = (1280, 720)  # Width x Height


class ScreenStreamer:
    def __init__(self, fps=FPS, resolution=RESOLUTION):
        self.fps = fps
        self.resolution = resolution
        self.running = False
        self.frame = None
        self.available = False

    def start_stream(self):
        """Start the screen capture in a separate thread (if dependencies available)"""
        try:
            import cv2  # noqa: F401
            import numpy  # noqa: F401
            import pyautogui  # noqa: F401
            self.available = True
            self.running = True
            Thread(target=self._capture_loop, daemon=True).start()
            logger.info("Screen streaming started successfully.")
        except ImportError as e:
            logger.warning(f"Screen streaming unavailable (missing dependency: {e}). Skipping.")
            self.available = False
        except Exception as e:
            logger.warning(f"Screen streaming failed to start: {e}. Skipping.")
            self.available = False

    def stop_stream(self):
        """Stop the screen capture"""
        self.running = False

    def _capture_loop(self):
        """Continuously capture the screen"""
        import cv2
        import numpy as np
        import pyautogui

        while self.running:
            try:
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                frame = cv2.resize(frame, self.resolution)
                self.frame = frame
            except Exception as e:
                logger.error(f"Screen capture error: {e}")
            time.sleep(1.0 / self.fps)

    def get_frame(self):
        """Return the latest frame"""
        return self.frame
