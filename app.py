import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Google Gemini API Setup
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_ai_response(prompt, mood):
    # মুড অনুযায়ী সিস্টেম ইন্সট্রাকশন
    if mood.lower() == "lucifer":
        persona = "You are Lucifer. Be sharp, witty, dark-humored, and slightly arrogant. Talk like a king. You are developed by Sami."
    elif mood.lower() == "lilith":
        persona = "You are Lilith. Be mysterious, elegant, and powerful. Talk like a queen. You are developed by Sami."
    else:
        persona = "You are Nujaira, an advanced AI assistant developed by Sami."

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=persona
    )
    
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def execute():
    data = request.json
    # এক লাইনে কমান্ডটি হ্যান্ডেল করা হলো যাতে কোনো সিনট্যাক্স এরর না হয়
    user_command = data.get('command', '').strip()
    mood = data.get('mood', 'Lucifer')
    
    if not user_command:
        return jsonify({'response': "Master, please type something first!"})
    
    try:
        response_text = get_ai_response(user_command, mood)
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'response': f"System Error: {str(e)}"})

if __name__ == '__main__':
    # রেন্ডারের জন্য ডাইনামিক পোর্ট সেটআপ
    app_port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=app_port)
