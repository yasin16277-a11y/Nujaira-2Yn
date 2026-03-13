import speech_recognition as sr
from langdetect import detect

# ===========================
# Voice Module Settings
# ===========================


def process_voice_input(duration=5, language='auto'):
    """
    Capture voice input from the microphone and convert to text.

    Parameters:
    - duration: maximum recording time in seconds
    - language: 'auto' to detect language automatically, or pass language code (e.g., 'en', 'bn', 'hi')

    Returns:
    - detected_text: string of recognized speech
    - detected_lang: detected language code
    """

    recognizer = sr.Recognizer()
    detected_text = ""
    detected_lang = language

    try:
        with sr.Microphone() as source:
            print(f"Listening for {duration} seconds...")
            audio = recognizer.listen(source, timeout=duration)

        # Recognize speech using Google's Speech Recognition
        detected_text = recognizer.recognize_google(audio)

        # Language detection if set to auto
        if language == 'auto':
            detected_lang = detect(detected_text)

    except sr.UnknownValueError:
        detected_text = ""
        print("Voice could not be understood.")
    except sr.RequestError as e:
        detected_text = ""
        print(f"Could not request results from service; {e}")
    except Exception as e:
        detected_text = ""
        print(f"Unexpected error: {e}")

    return detected_text, detected_lang
