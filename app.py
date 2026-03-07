import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Google Gemini API Setup
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_ai_response(prompt, mood):
    mood_lower = mood.lower()
    if mood_lower == "lucifer":
        persona = "You are Lucifer. Be sharp, witty, dark-humored, and slightly arrogant. Talk like a king. You are developed by Mohammad Yasin Sojib."
    elif mood_lower == "lilith":
        persona = "You are Lilith. Be mysterious, elegant, and powerful. Talk like a queen. You are developed by Mohammad Yasin Sojib."
    else:
        persona = "You are Nujaira, a highly advanced AI assistant developed by Mohammad Yasin Sojib."

    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=persona)
    response = model.generate_content(prompt)
    return response.text if response else "AI could not generate a response."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def execute():
    try:
        # ফ্রন্টএন্ড থেকে আসা ডাটা রিসিভ করা (JSON বা Form যাই হোক)
        data = request.get_json(silent=True) or request.form.to_dict()
        
        # 'command' বা 'text' বা 'message' যে নামেই আসুক, ডাটা খুঁজে নিবে
        user_command = data.get('command') or data.get('text') or data.get('message') or ""
        user_command = str(user_command).strip()
        mood = data.get('mood', 'Lucifer')
        
        if not user_command:
            return jsonify({'response': "Master, please type something first!"})

        response_text = get_ai_response(user_command, mood)
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'response': f"System Error: {str(e)}"})

if __name__ == '__main__':
    # রেন্ডারের জন্য পোর্ট কনফিগারেশন
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)