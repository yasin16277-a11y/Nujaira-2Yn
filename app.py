from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import ast
from persona_manager import get_system_prompt

load_dotenv()

app = Flask(__name__, template_folder='templates') 
CORS(app)

API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")

def secure_math_solver(expression):
    try:
        node = ast.parse(expression, mode='eval')
        code = compile(node, '<string>', 'eval')
        return eval(code, {"__builtins__": None}, {})
    except Exception:
        return "Math Error: Invalid Expression"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get("message", "")
    current_mood = data.get("mood", "default")
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    system_prompt = get_system_prompt(current_mood)
    
    if "delete system" in user_message.lower() or "shutdown" in user_message.lower():
        return jsonify({
            "response": "Access Denied: Admin authorization required for system-level modifications.",
            "mood_status": current_mood
        }), 403

    if "calculate" in user_message.lower():
        math_expr = user_message.replace("calculate", "").strip()
        result = secure_math_solver(math_expr)
        return jsonify({"response": f"The result is: {result}"})

    ai_reply = f"[{current_mood.upper()} MODE] I received your command: '{user_message}'. Awaiting LLM integration to process."

    return jsonify({"response": ai_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
