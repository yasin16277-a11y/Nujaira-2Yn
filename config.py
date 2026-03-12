import os

# ===========================
# API KEYS / CONFIGURATION
# ===========================

# OpenAI API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key-here")

# Voice Module Settings (placeholder)
VOICE_ENABLED = True            # Enable voice recognition
VOICE_LANGUAGE = "auto"         # Auto-detect user language (bn, hi, en)

# Screen Streaming / Capture Settings
SCREEN_STREAM_ENABLED = True    # Enable screen capture/streaming
SCREEN_STREAM_FPS = 15          # Frames per second
SCREEN_STREAM_RESOLUTION = (1280, 720)  # Width x Height

# Session Memory Settings
SESSION_MEMORY_ENABLED = True   # In-memory temporary memory
SESSION_MEMORY_MAX_ENTRIES = 100  # Max messages stored per user

# Logging / Debug
DEBUG_MODE = False
LOG_FILE = "nujaira2_logs.txt"

# Feature Toggles
ROLEPLAY_MODE_ENABLED = True
FANTASY_MODE_ENABLED = True
PERSONA_MODES = ["default", "lucifer", "lilith", "kamukta", "fantasy", "roleplay", "mom"]

# Misc
PORT = int(os.environ.get("PORT", 10000))
HOST = '0.0.0.0'

# ===========================
# Ensure keys are present
# ===========================
if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
    raise ValueError("OpenAI API Key is not set! Please set the environment variable 'OPENAI_API_KEY'.")