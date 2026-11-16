from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

print("Anfrage wird gesendet ...")

response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents="Erkläre Django in einem kurzen Satz."
)

print(response.text)