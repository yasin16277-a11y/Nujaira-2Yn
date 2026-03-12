# memory_manager.py

class MemoryManager:
    def __init__(self):
        # In-memory store for sessions: {session_id: [history]}
        self.sessions = {}

    def get_context(self, session_id):
        """
        Return concatenated context for a session.
        """
        if session_id in self.sessions:
            return "\n".join(self.sessions[session_id])
        return ""

    def update_memory(self, session_id, user_input, ai_response):
        """
        Add user input and AI response to session memory.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append(f"User: {user_input}")
        self.sessions[session_id].append(f"AI: {ai_response}")

        # Optional: limit memory size to avoid excessive growth
        max_len = 50  # keep last 50 entries
        if len(self.sessions[session_id]) > max_len:
            self.sessions[session_id] = self.sessions[session_id][-max_len:]

    def clear_memory(self, session_id):
        """
        Clear session memory on-demand.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def forget_partial(self, session_id, keywords):
        """
        Remove memory entries containing any of the keywords.
        """
        if session_id not in self.sessions:
            return
        self.sessions[session_id] = [
            entry for entry in self.sessions[session_id]
            if not any(kw.lower() in entry.lower() for kw in keywords)
        ]