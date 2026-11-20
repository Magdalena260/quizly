import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_quiz_questions(topic):
    prompt = f"""
    Erstelle 3 Quizfragen zum Thema "{topic}".

    Regeln:
    - Jede Frage soll 4 Antwortmöglichkeiten haben.
    - Gib die richtige Antwort mit an.
    - Antworte klar und übersichtlich.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    return response.text