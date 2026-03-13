import os

# ===========================
# API KEYS / CONFIGURATION
# ===========================

# Google Generative AI (Gemini) API Key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Gemini Model Settings
GEMINI_MODEL = "gemini-1.5-flash"

# Voice Module Settings
VOICE_ENABLED = True            # Enable voice recognition
VOICE_LANGUAGE = "auto"         # Auto-detect user language (bn, hi, en)

# Screen Streaming / Capture Settings
SCREEN_STREAM_ENABLED = os.environ.get("SCREEN_STREAM_ENABLED", "false").lower() == "true"
SCREEN_STREAM_FPS = 15          # Frames per second
SCREEN_STREAM_RESOLUTION = (1280, 720)  # Width x Height

# Session Memory Settings
SESSION_MEMORY_ENABLED = True   # In-memory temporary memory
SESSION_MEMORY_MAX_ENTRIES = 100  # Max messages stored per user

# Logging / Debug
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
LOG_FILE = "nujaira2_logs.txt"

# Feature Toggles
ROLEPLAY_MODE_ENABLED = True
FANTASY_MODE_ENABLED = True
PERSONA_MODES = ["default", "lucifer", "lilith", "kamukta", "fantasy", "roleplay", "mom"]

# Misc
PORT = int(os.environ.get("PORT", 10000))
HOST = '0.0.0.0'
