import os
import uuid
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", str(uuid.uuid4()))

# OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# -------------------------
# Temporary in-memory session
# -------------------------
user_sessions = {}

def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    return user_sessions[user_id]

# -------------------------
# AI response
# -------------------------
def get_ai_response(prompt, mood, user_id=None):
    persona_dict = {
        "lucifer": "You are Lucifer. Sharp, witty, dark-humored, slightly arrogant. Talk like a king.",
        "lilith": "You are Lilith. Mysterious, elegant, powerful. Talk like a queen.",
        "nujaira": "You are Nujaira, a highly advanced AI assistant."
    }
    persona = persona_dict.get(mood.lower(), persona_dict["nujaira"])
    
    messages = [{"role": "system", "content": persona}]
    if user_id:
        messages += get_user_session(user_id)
    messages.append({"role": "user", "content": prompt})

    try:
        response = openai.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.7,
            max_tokens=1200
        )
        ai_text = response.choices[0].message.content.strip()
        # Remember command-dependent memory
        if user_id and "remember this" in prompt.lower():
            get_user_session(user_id).append({"role": "user", "content": prompt})
            get_user_session(user_id).append({"role": "assistant", "content": ai_text})
        return ai_text
    except Exception as e:
        return f"AI System Error: {str(e)}"

# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or request.form.to_dict()
    user_command = data.get('command') or data.get('text') or data.get('message') or ""
    mood = data.get('mood', 'Lucifer')
    user_id = data.get('user_id') or str(uuid.uuid4())

    if not user_command:
        return jsonify({'response': "Please type something!", 'user_id': user_id})

    cmd_lower = user_command.lower()
    # Forget / Clear hooks
    if "forget last topic" in cmd_lower and user_id in user_sessions:
        if len(user_sessions[user_id]) >= 2:
            user_sessions[user_id] = user_sessions[user_id][:-2]
        return jsonify({'response': "Last topic forgotten.", 'user_id': user_id})
    elif "clear all memory" in cmd_lower and user_id in user_sessions:
        user_sessions[user_id] = []
        return jsonify({'response': "All memory cleared.", 'user_id': user_id})

    ai_response = get_ai_response(user_command, mood, user_id)
    return jsonify({'response': ai_response, 'user_id': user_id})

# -------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)