
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
- Error handling for unavailable YouTube downloads and AI services

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

- Python compatible with the project dependencies
- pip
- FFmpeg installed and available in the system PATH
- Google Gemini API key
- Internet connection

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Magdalena260/quizly.git
cd quizly
```

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
python -m pip install -r requirements.txt
```

FFmpeg must be installed separately and available in the system PATH.

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your_django_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder values with your own credentials.

Never commit real API keys or secrets to GitHub.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available locally at:

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

A successful generation creates a quiz containing three questions. Each question has four answer options and one correct answer.

## Quiz Generation Workflow

1. An authenticated user submits a YouTube video URL.
2. yt-dlp downloads the video's audio.
3. FFmpeg converts the audio into MP3 format.
4. OpenAI Whisper transcribes the spoken content.
5. Google Gemini generates quiz questions from the transcript.
6. Django saves the quiz and its questions to the database.
7. The API returns the generated quiz as JSON.

## Error Handling

Quiz generation depends on external services and may fail if YouTube or Gemini is unavailable.

| HTTP Status | Description |
|-------------|-------------|
| 201 Created | Quiz generated successfully |
| 400 Bad Request | Invalid or missing request data |
| 401 Unauthorized | Authentication required |
| 502 Bad Gateway | YouTube download failed |
| 503 Service Unavailable | Gemini is temporarily unavailable |

YouTube may restrict automated downloads or request additional authentication.

If YouTube blocks the download, the API returns a controlled error response instead of an unhandled server exception.

Example:

```json
{
  "detail": "The YouTube video could not be downloaded. Please try again later."
}
```

## Automated Tests

The project includes 22 automated API tests across two Django applications:

- 13 quiz API tests
- 9 authentication API tests

Run all tests with:

```bash
python manage.py test
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
- Error handling when a YouTube download fails

Quiz generation is mocked in the automated API tests. A successful end-to-end live test depends on YouTube access and Gemini availability.

## Security

- API keys and secrets are loaded from environment variables.
- JWT authentication uses HttpOnly cookies.
- Quiz endpoints require authentication.
- Users can only view their own quizzes in the quiz list.
- Users cannot update or delete another user's quiz.
- `.env`, `.venv`, and `db.sqlite3` are excluded from Git tracking through `.gitignore`.

## Project Status

The backend includes authentication, quiz management, and AI-based quiz generation.

**Automated test results: 22 tests passed, 0 failures.**

The live YouTube download is currently restricted by YouTube's automated access protection. The API handles this failure with HTTP 502.
