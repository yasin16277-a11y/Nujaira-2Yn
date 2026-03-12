import os
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
from persona_manager import get_system_prompt
import google.generativeai as genai
from voice_module import process_voice_input
from screen_stream import ScreenStreamer
import cv2
import threading
import io

app = Flask(__name__)
CORS(app)

# ===========================
# Google Generative AI API Setup
# ===========================
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_ai_response(prompt, mood):
    persona = get_system_prompt(mood)
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=persona)
        response = model.generate_content(prompt)
        return response.text if response else "AI could not generate a response."
    except Exception as e:
        return f"AI System Error: {str(e)}"

# ===========================
# Screen Stream Setup
# ===========================
screen_streamer = ScreenStreamer()
screen_streamer.start_stream()

@app.route('/')
def index():
    return render_template('index.html')

# ===========================
# Chat API Endpoint
# ===========================
@app.route('/api/chat', methods=['POST'])
def execute():
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        user_command = data.get('command') or data.get('text') or data.get('message') or ""
        user_command = str(user_command).strip()
        mood = data.get('mood', 'default')
        if not user_command:
            return jsonify({'response': "Master, please type something first!"})
        response_text = get_ai_response(user_command, mood)
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'response': f"System Error: {str(e)}"})

# ===========================
# Voice Input Endpoint
# ===========================
@app.route('/api/voice', methods=['GET'])
def voice_input():
    try:
        text, lang = process_voice_input()
        return jsonify({'voice_text': text, 'language': lang})
    except Exception as e:
        return jsonify({'voice_text': '', 'language': '', 'error': str(e)})

# ===========================
# Screen Capture Endpoint
# ===========================
@app.route('/api/screen', methods=['GET'])
def get_screen_frame():
    try:
        frame = screen_streamer.get_frame()
        if frame is None:
            return Response(status=204)
        _, buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(buffer)
        return send_file(io_buf, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)})

# ===========================
# Graceful Shutdown
# ===========================
def shutdown_streamer():
    screen_streamer.stop_stream()

import atexit
atexit.register(shutdown_streamer)

# ===========================
# Run Flask App
# ===========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)