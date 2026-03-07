@app.route('/api/chat', methods=['POST'])
def execute():
    data = request.json
    # নিশ্চিত করা হচ্ছে যে কমান্ডটি খালি নয়
    command = data.get('command', '').strip() 
    mood = data.get('mood', 'Lucifer')
    
    if not command:
        return jsonify({'response': "Master, please type something first!"})
    
    try:
        response = get_ai_response(command, mood)
        if not response:
            return jsonify({'response': "AI is silent. Check API logs."})
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"System Error: {str(e)}"})
