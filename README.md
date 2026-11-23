
# Quizly – AI-Powered Quiz Generator

Quizly is a REST API that automatically generates quizzes from YouTube videos using artificial intelligence.

The backend is built with Django and Django REST Framework.

## Features

- User registration and login
- JWT authentication using HttpOnly cookies
- Automatic quiz generation from YouTube videos
- Audio extraction using yt-dlp
- Audio transcription using OpenAI Whisper
- Quiz question generation using Google Gemini
- Storage of quizzes, questions, and answer options
- Retrieve, update, and delete personal quizzes
- Access protection for quizzes owned by other users

## Technologies

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite
- Google Gemini API
- OpenAI Whisper
- yt-dlp
- FFmpeg
- python-dotenv

## Requirements

- Python
- pip
- FFmpeg
- Google Gemini API key
- Internet connection

## Installation

### 1. Clone the repository

```bash
git clone <REPOSITORY-URL>
cd quizly
```

Replace the placeholder with the actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

FFmpeg must also be installed and available in the system PATH.

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your_django_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

Never commit real API keys or secrets to GitHub.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

`http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register a new user |
| POST | `/api/login/` | Log in and set JWT cookies |
| POST | `/api/logout/` | Log out and clear authentication cookies |
| POST | `/api/token/refresh/` | Refresh the access token |

Example registration request:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePassword123!",
  "confirmed_password": "SecurePassword123!"
}
```

Example login request:

```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```

### Quiz Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quizzes/` | Retrieve the authenticated user's quizzes |
| POST | `/api/quizzes/` | Generate a quiz from a YouTube video |
| GET | `/api/quizzes/{id}/` | Retrieve a specific quiz |
| PATCH | `/api/quizzes/{id}/` | Update a quiz's title or description |
| DELETE | `/api/quizzes/{id}/` | Delete a quiz |

Example quiz generation request:

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

A successful generation creates a quiz containing three questions, each with four answer options and one correct answer.

## Quiz Generation Workflow

1. An authenticated user submits a YouTube video URL.
2. yt-dlp downloads the video's audio.
3. FFmpeg converts the audio into MP3 format.
4. OpenAI Whisper transcribes the spoken content.
5. Google Gemini generates quiz questions from the transcript.
6. Django saves the quiz and its questions to the database.
7. The API returns the generated quiz as JSON.

**Note:** Quiz generation depends on external services. If Gemini is temporarily unavailable, the API may return HTTP 503.

## Automated Tests

The project includes 21 automated API tests across two Django applications.

Run the tests with:

```bash
python manage.py test quiz_app auth_app
```

The tests cover:

- User registration and validation
- Login and invalid credentials
- JWT cookie handling
- Token refresh
- Logout
- Quiz creation
- Quiz retrieval and updates
- Quiz deletion
- Authentication and object-level permissions
- Error handling when Gemini is unavailable

Quiz generation is mocked in the automated API tests. A complete live test with YouTube, Whisper, and Gemini must be performed separately.

## Security

- API keys and secrets are loaded from environment variables.
- JWT authentication uses HttpOnly cookies.
- Quiz endpoints require authentication.
- Users can only view their own quizzes in the quiz list.
- Users cannot update or delete another user's quiz.
- `.env`, `.venv`, and `db.sqlite3` are excluded from future Git tracking through `.gitignore`.

## Project Status

The backend includes authentication, quiz management, and AI-based quiz generation.

**Automated test results: 21 tests passed, 0 failures.**
