# Quizly – AI-Powered Quiz Generator

Quizly is a REST API that automatically generates quizzes from YouTube videos using artificial intelligence.

The backend is built with Django and Django REST Framework.

## Features

- User registration and login
- JWT authentication using HttpOnly cookies
- Access and refresh token invalidation after logout
- Automatic quiz generation from YouTube videos
- Audio extraction using yt-dlp and FFmpeg
- Audio transcription using OpenAI Whisper
- Quiz question generation using Google Gemini
- Generation of exactly 10 questions per quiz
- Four answer options and one correct answer per question
- Validation of AI-generated quiz data
- Storage of quizzes, questions, and answer options
- Retrieval, updating, and deletion of personal quizzes
- Object-level access protection
- Django Admin management of quizzes and questions
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

The Django Admin interface is available at:

`http://127.0.0.1:8000/admin/`

To create an administrator account, run:

```bash
python manage.py createsuperuser
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Register a new user |
| POST | `/api/login/` | Log in and set JWT

## Final Test Results

- 39 automated tests passed
- 11 authentication tests
- 28 quiz and service tests
- 99% code coverage
- Flake8 checks passed

Run the tests:

    python manage.py test

Measure code coverage:

    python -m coverage run --source=auth_app,quiz_app manage.py test
    python -m coverage report -m

The live YouTube download and Whisper transcription were tested
successfully.

The full Gemini live generation remains unverified because the
Google Gemini API returned HTTP 503.