import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("API-Key gefunden:", bool(api_key))

client = genai.Client(api_key=api_key)

prompt = """
Erstelle 3 Quizfragen mit jeweils 4 Antwortmöglichkeiten.
Markiere außerdem die richtige Antwort.

Thema:
Der Herr der Ringe
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt,
)

print(response.text)