import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_quiz_questions(topic):
    prompt = f"""
    Erstelle ein Quiz zum folgenden Inhalt:

    {topic}

    Erstelle 3 Quizfragen mit jeweils 4 Antwortmöglichkeiten.

    Verwende exakt diese JSON-Struktur:

    {{
        "title": "Quiztitel",
        "description": "Kurze Beschreibung",
        "questions": [
            {{
                "question_title": "Frage",
                "question_options": [
                    "Antwort 1",
                    "Antwort 2",
                    "Antwort 3",
                    "Antwort 4"
                ],
                "answer": "Antwort 1"
            }}
        ]
    }}

    Die richtige Antwort muss exakt einer der
    vier Antwortmöglichkeiten entsprechen.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    return json.loads(response.text)