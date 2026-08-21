from backend.app.harness.interaction import (
    conversational_answer,
    detect_language,
    is_conversational,
    resolve_language,
)


def test_supported_language_detection():
    assert detect_language("What is a corporation?") == "en-IN"
    assert detect_language("कॉर्पोरेशन क्या है?") == "hi-IN"
    assert detect_language("कॉर्पोरेशन काय आहे?") == "mr-IN"


def test_selected_language_is_used_for_latin_input():
    assert resolve_language("What is a corporation?", "mr-IN") == "mr-IN"
    assert resolve_language("कॉर्पोरेशन क्या है?", "en-IN") == "hi-IN"


def test_greeting_and_introduction_are_conversational():
    assert is_conversational("Hi")
    assert is_conversational("Hi, I'm Akshata")
    assert is_conversational("नमस्कार")
    assert is_conversational("How are you?")
    assert not is_conversational("What is a corporation?")
    assert conversational_answer("Hi, I'm Akshata", "en-IN") == "Hi, Akshata! How can I help?"
