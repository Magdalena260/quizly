
## Automated Tests

The project includes 27 automated tests:

- 11 authentication API tests
- 16 quiz API and validation tests

The tests cover:

- User registration and login
- JWT authentication using HttpOnly cookies
- Token refresh and logout
- Access and refresh token invalidation after logout
- Quiz creation with exactly 10 questions
- Four answer options per question
- Quiz retrieval, updating, and deletion
- Authentication and object-level permissions
- Rejection of non-YouTube URLs
- Validation of generated quiz data
- Error handling for YouTube and Gemini failures

Run the automated tests:

```bash
python manage.py test
```

Latest verified result: 27 tests passed, 0 failures.

The quiz generation tests use mocked AI responses.
The complete Gemini live generation test remains
unverified because the API returned HTTP 503.
