import os
import io
import uuid
import time
import logging
import atexit
from collections import defaultdict
from functools import wraps

from flask import Flask, render_template, request, jsonify, send_file, Response, session
from flask_cors import CORS
from persona_manager import get_system_prompt
from memory_manager import MemoryManager
from screen_stream import ScreenStreamer
from config import (
    GOOGLE_API_KEY, GEMINI_MODEL, SCREEN_STREAM_ENABLED,
    PORT, HOST, PERSONA_MODES,
    RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW,
    MAX_INPUT_LENGTH, ALLOWED_ORIGINS,
)

import google.generativeai as genai

# ===========================
# Logging Setup
# ===========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ===========================
# Flask App Setup
# ===========================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB max request size
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("HTTPS_ENABLED", "false").lower() == "true"

cors_origins = ALLOWED_ORIGINS if ALLOWED_ORIGINS else "*"
CORS(app, origins=cors_origins, supports_credentials=True)


# ===========================
# Security: Rate Limiter
# ===========================
class RateLimiter:
    """Simple in-memory rate limiter per IP address."""

    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key):
        now = time.time()
        window_start = now - self.window
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        if len(self.requests[key]) >= self.max_requests:
            return False
        self.requests[key].append(now)
        return True


rate_limiter = RateLimiter(max_requests=RATE_LIMIT_REQUESTS, window_seconds=RATE_LIMIT_WINDOW)


def rate_limit(f):
    """Decorator to enforce rate limiting on endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({"error": "Too many requests. Please slow down."}), 429
        return f(*args, **kwargs)
    return decorated


# ===========================
# Security: Response Headers
# ===========================
@app.after_request
def set_security_headers(response):
    """Inject security headers into every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=(), microphone=(self)"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' blob: data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    return response


# ===========================
# Security: Input Sanitization
# ===========================
def sanitize_input(text, max_length=None):
    """Sanitize and validate user input."""
    if not isinstance(text, str):
        return ""
    text = text.strip()
    limit = max_length or MAX_INPUT_LENGTH
    if len(text) > limit:
        text = text[:limit]
    return text


def validate_persona(mood):
    """Validate that the requested persona is allowed."""
    if mood not in PERSONA_MODES:
        return "default"
    return mood


# ===========================
# Google Generative AI Setup
# ===========================
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    logger.info("Google Generative AI configured successfully.")
else:
    logger.warning("GOOGLE_API_KEY not set. AI responses will not work.")

# ===========================
# Memory Manager
# ===========================
memory = MemoryManager()

# ===========================
# Screen Stream Setup (conditional)
# ===========================
screen_streamer = ScreenStreamer()
if SCREEN_STREAM_ENABLED:
    screen_streamer.start_stream()


def get_session_id():
    """Get or create a unique session ID for the current user."""
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


def get_ai_response(prompt, mood, session_id):
    """Generate AI response with conversation memory context."""
    persona = get_system_prompt(mood)
    context = memory.get_context(session_id)

    full_prompt = prompt
    if context:
        full_prompt = f"Previous conversation:\n{context}\n\nUser: {prompt}"

    try:
        model = genai.GenerativeModel(model_name=GEMINI_MODEL, system_instruction=persona)
        response = model.generate_content(full_prompt)
        response_text = response.text if response else "I couldn't generate a response. Please try again."
        memory.update_memory(session_id, prompt, response_text)
        return response_text
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return "I encountered an issue generating a response. Please try again."


# ===========================
# Routes
# ===========================
@app.route("/")
def index():
    return render_template("index.html", persona_modes=PERSONA_MODES)


@app.route("/api/chat", methods=["POST"])
@rate_limit
def chat():
    """Handle chat messages with memory context."""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        user_command = data.get("command") or data.get("text") or data.get("message") or ""
        user_command = sanitize_input(str(user_command))
        mood = validate_persona(data.get("mood", "default"))

        if not user_command:
            return jsonify({"response": "Please type a message to get started.", "status": "empty"})

        session_id = get_session_id()
        response_text = get_ai_response(user_command, mood, session_id)

        return jsonify({"response": response_text, "status": "success"})
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"response": "An unexpected error occurred. Please try again.", "status": "error"})


@app.route("/api/clear", methods=["POST"])
@rate_limit
def clear_memory():
    """Clear conversation memory for the current session."""
    try:
        session_id = get_session_id()
        memory.clear_memory(session_id)
        return jsonify({"status": "success", "message": "Conversation cleared."})
    except Exception as e:
        logger.error(f"Clear memory error: {e}")
        return jsonify({"status": "error", "message": "Failed to clear conversation."})


@app.route("/api/personas", methods=["GET"])
def get_personas():
    """Return available persona modes."""
    return jsonify({"personas": PERSONA_MODES})


@app.route("/api/voice", methods=["GET"])
@rate_limit
def voice_input():
    """Handle voice input capture."""
    try:
        from voice_module import process_voice_input
        text, lang = process_voice_input()
        return jsonify({"voice_text": sanitize_input(text), "language": lang})
    except ImportError:
        return jsonify({"voice_text": "", "language": "", "error": "Voice module not available"})
    except Exception as e:
        logger.error(f"Voice input error: {e}")
        return jsonify({"voice_text": "", "language": "", "error": "Voice processing failed."})


@app.route("/api/screen", methods=["GET"])
@rate_limit
def get_screen_frame():
    """Return current screen capture frame."""
    if not screen_streamer.available:
        return jsonify({"error": "Screen streaming not available"}), 503

    try:
        frame = screen_streamer.get_frame()
        if frame is None:
            return Response(status=204)
        import cv2
        _, buffer = cv2.imencode(".jpg", frame)
        io_buf = io.BytesIO(buffer)
        return send_file(io_buf, mimetype="image/jpeg")
    except Exception as e:
        logger.error(f"Screen frame error: {e}")
        return jsonify({"error": "Screen capture failed."})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "ai_configured": bool(GOOGLE_API_KEY),
        "screen_stream": screen_streamer.available,
    })


# ===========================
# Graceful Shutdown
# ===========================
def shutdown_streamer():
    screen_streamer.stop_stream()


atexit.register(shutdown_streamer)

# ===========================
# Run Flask App
# ===========================
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=os.environ.get("DEBUG_MODE", "false").lower() == "true")
