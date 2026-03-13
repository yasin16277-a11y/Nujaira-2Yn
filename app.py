import os
import io
import uuid
import logging
import atexit

from flask import Flask, render_template, request, jsonify, send_file, Response, session
from flask_cors import CORS
from persona_manager import get_system_prompt
from memory_manager import MemoryManager
from screen_stream import ScreenStreamer
from config import GOOGLE_API_KEY, GEMINI_MODEL, SCREEN_STREAM_ENABLED, PORT, HOST, PERSONA_MODES

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
CORS(app)

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
        return f"AI System Error: {str(e)}"


# ===========================
# Routes
# ===========================
@app.route("/")
def index():
    return render_template("index.html", persona_modes=PERSONA_MODES)


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages with memory context."""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        user_command = data.get("command") or data.get("text") or data.get("message") or ""
        user_command = str(user_command).strip()
        mood = data.get("mood", "default")

        if not user_command:
            return jsonify({"response": "Please type a message to get started.", "status": "empty"})

        session_id = get_session_id()
        response_text = get_ai_response(user_command, mood, session_id)

        return jsonify({"response": response_text, "status": "success"})
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"response": f"System Error: {str(e)}", "status": "error"})


@app.route("/api/clear", methods=["POST"])
def clear_memory():
    """Clear conversation memory for the current session."""
    try:
        session_id = get_session_id()
        memory.clear_memory(session_id)
        return jsonify({"status": "success", "message": "Conversation cleared."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/personas", methods=["GET"])
def get_personas():
    """Return available persona modes."""
    return jsonify({"personas": PERSONA_MODES})


@app.route("/api/voice", methods=["GET"])
def voice_input():
    """Handle voice input capture."""
    try:
        from voice_module import process_voice_input
        text, lang = process_voice_input()
        return jsonify({"voice_text": text, "language": lang})
    except ImportError:
        return jsonify({"voice_text": "", "language": "", "error": "Voice module not available"})
    except Exception as e:
        return jsonify({"voice_text": "", "language": "", "error": str(e)})


@app.route("/api/screen", methods=["GET"])
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
        return jsonify({"error": str(e)})


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
