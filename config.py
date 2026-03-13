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

# Security Settings
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", 30))  # Max requests per window
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))  # Window in seconds
MAX_INPUT_LENGTH = int(os.environ.get("MAX_INPUT_LENGTH", 5000))  # Max chars per message
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",") if os.environ.get("ALLOWED_ORIGINS") else []

# Misc
PORT = int(os.environ.get("PORT", 10000))
HOST = '0.0.0.0'
