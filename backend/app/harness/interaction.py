"""Cheap input classification and language resolution for a pipeline turn."""

from __future__ import annotations

import re

SUPPORTED_LANGUAGES = {"en-IN", "hi-IN", "mr-IN"}

_DEVANAGARI = re.compile(r"[\u0900-\u097f]")
_MARATHI_MARKERS = {
    "आहे", "आहेत", "काय", "माझ", "माझं", "माझे", "नमस्कार", "धन्यवाद",
    "कुठे", "कधी", "कोणते", "करू", "माहिती", "सांगा",
}
_HINDI_MARKERS = {
    "है", "हैं", "क्या", "मेरा", "मेरी", "नमस्ते", "धन्यवाद", "कहाँ",
    "कब", "कौन", "बताओ", "बताइए", "जानकारी",
}


def detect_language(query: str) -> str:
    """Detect the supported script/language without a network call."""
    if not _DEVANAGARI.search(query):
        return "en-IN"
    words = set(re.findall(r"[\u0900-\u097f]+", query))
    marathi = len(words & _MARATHI_MARKERS)
    hindi = len(words & _HINDI_MARKERS)
    return "mr-IN" if marathi > hindi else "hi-IN"


def resolve_language(query: str, selected: str | None) -> str:
    """Honor an explicit selector; an omitted/invalid selection defaults to English."""
    return selected if selected in SUPPORTED_LANGUAGES else "en-IN"


def is_conversational(query: str) -> bool:
    """Recognize greetings, thanks, farewells and short self-introductions."""
    text = " ".join(query.lower().strip().split())
    patterns = (
        r"^(hi|hello|hey|good (morning|afternoon|evening))[!. ]*$",
        r"^(hi|hello|hey)[,!. ]+(i am|i'm|my name is)\b",
        r"^(i am|i'm|my name is)\s+[\w .'-]+[!.]*$",
        r"^(thanks|thank you|bye|goodbye)[!. ]*$",
        r"^(how are you|how's it going|nice to meet you)[?!. ]*$",
        r"^(नमस्ते|नमस्कार|धन्यवाद)[।!. ]*$",
        r"^(आप कैसे हैं|तुम कैसे हो|तुम्ही कसे आहात|कसे आहात)[?।!. ]*$",
        r"^(मेरा नाम|मेरी नाम|माझे नाव|माझं नाव)\s+.+$",
    )
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def conversational_answer(query: str, language_code: str) -> str:
    name_match = re.search(
        r"(?:i am|i'm|my name is)\s+([\w'-]+)|(?:मेरा नाम|माझे नाव|माझं नाव)\s+([^,.!।]+)",
        query,
        flags=re.IGNORECASE,
    )
    name = next((part.strip() for part in (name_match.groups() if name_match else ()) if part), "")
    if language_code == "hi-IN":
        return f"नमस्ते{', ' + name if name else ''}! मैं आपकी कैसे मदद कर सकता हूँ?"
    if language_code == "mr-IN":
        return f"नमस्कार{', ' + name if name else ''}! मी तुम्हाला कशी मदत करू शकते?"
    return f"Hi{', ' + name if name else ''}! How can I help?"


__all__ = [
    "SUPPORTED_LANGUAGES", "detect_language", "resolve_language",
    "is_conversational", "conversational_answer",
]
