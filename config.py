# config.py

import os

# ==========================
# API Keys
# ==========================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "your_google_api_key_here")

# ==========================
# App Settings
# ==========================
APP_PORT = int(os.environ.get("PORT", 10000))
DEBUG_MODE = True

# Default session memory limit (number of entries per session)
SESSION_MEMORY_LIMIT = 50

# Supported languages for TTS / voice
SUPPORTED_LANGUAGES = ['en', 'bn', 'hi']

# Enable / Disable optional modules
ENABLE_VOICE_MODULE = True
ENABLE_SCREEN_STREAM = True

# ==========================
# Future placeholders for cloud storage, logging, etc.
# ==========================
CLOUD_BACKUP_ENABLED = False
LOGGING_ENABLED = True