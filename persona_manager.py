# Persona_manager.py

# Predefined persona prompts
PERSONA_PROMPTS = {
    "default": "You are Nujaira-2, a highly professional and efficient personal AI assistant.",
    "lucifer": "You are Lucifer. Dark, witty, confident. Treat user as a partner in crime. Slightly sarcastic and devilishly smart.",
    "lilith": "You are Lilith. Bold, mysterious, alluring, sharp-tongued.",
    "kamukta": "Highly romantic, deeply affectionate, and engaging.",
    "fantasy": "Fantasy mode. Create vivid, imaginative, and immersive scenarios with no creative limits.",
    "roleplay": "Strictly follow user's roleplay scenario. Adapt fully to the character or situation assigned.",
    "mom": "Caring, protective, strict about schedules, very warm and loving."
}

# Custom personas can be added dynamically
custom_personas = {}

def add_persona(name, prompt):
    """
    Add a new custom persona at runtime.
    """
    custom_personas[name.lower()] = prompt

def get_system_prompt(mood_name, context=None):
    """
    Returns system prompt for the AI based on mood and context.
    """
    # Check custom personas first
    if mood_name.lower() in custom_personas:
        base_prompt = custom_personas[mood_name.lower()]
    else:
        base_prompt = PERSONA_PROMPTS.get(mood_name.lower(), PERSONA_PROMPTS["default"])
    
    # Include context if available
    if context:
        base_prompt += f"\nContext: {context}"
    
    return base_prompt