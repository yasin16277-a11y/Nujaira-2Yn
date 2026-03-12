import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from Persona_manager import get_system_prompt
from memory_manager import MemoryManager

# Optional modules placeholders
# from voice_module import process_voice_input, generate_tts
# from screen_stream import process_screen_context

app = Flask(__name__)
CORS(app)

# Session Memory Manager
memory = MemoryManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Receive frontend data (JSON or Form)
        data = request.get_json(silent=True) or request.form.to_dict()
        user_input = data.get('text') or data.get('message') or ""
        mood = data.get('mood', 'default')
        session_id = data.get('session_id', 'default_session')

        if not user_input:
            return jsonify({'response': "Please type something first!"})

        # Optionally handle voice input if provided
        # if 'voice_file' in data:
        #     user_input = process_voice_input(data['voice_file'])

        # Retrieve session context for memory
        context = memory.get_context(session_id)

        # Get persona system prompt
        system_prompt = get_system_prompt(mood, context)

        # Generate AI response placeholder (replace with actual API call, e.g., OpenAI)
        response_text = f"[AI Response based on: {system_prompt}] User said: {user_input}"

        # Update session memory
        memory.update_memory(session_id, user_input, response_text)

        # Optionally generate TTS
        # tts_audio_url = generate_tts(response_text)

        return jsonify({
            'response': response_text,
            # 'tts_url': tts_audio_url
        })

    except Exception as e:
        return jsonify({'response': f"System Error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)