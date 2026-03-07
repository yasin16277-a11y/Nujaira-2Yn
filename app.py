import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Google Gemini API Setup
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def get_ai_response(prompt, mood):
    # মুড অনুযায়ী ক্যারেক্টার সেট করা
    if mood.lower() == "lucifer":
        persona = "You are Lucifer. Be sharp, witty, dark-humored, and slightly arrogant. Talk like a king. You are part of Project Felicity developed by Sami."
    elif mood.lower() == "lilith":
        persona = "You are Lilith. Be mysterious, elegant, and powerful. Talk like a queen. You are part of Project Felicity developed by Sami."
    else:
        persona = "You are Nujaira, a highly advanced AI assistant developed by Sami."

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=persona
    )
    
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get('command')
    mood = data.get('mood', 'Lucifer')
    
    try:
        response = get_ai_response(command, mood)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"System Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
