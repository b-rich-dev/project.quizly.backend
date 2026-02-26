# Quizly Backend

Django REST API Backend for the Quizly application with YouTube video integration and AI-powered quiz generation.

## Features

- 🔐 JWT-based authentication with cookie support
- 📹 YouTube video transcription with Whisper AI
- 🤖 Automatic quiz generation with Google Gemini
- ✅ Complete test coverage

## Prerequisites

- Python 3.10+
- FFmpeg (for audio/video processing)
- Google Gemini API Key

## FFmpeg Installation

### Windows
```powershell
# Using Winget
winget install Gyan.FFmpeg

# Or manually from: https://ffmpeg.org/download.html
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

**FFmpeg PATH Configuration:**
- If FFmpeg is in system PATH: no additional configuration needed
- Otherwise: set `FFMPEG_PATH` in `.env` (see `.env.example`)

## Installation

1. **Clone repository**
```bash
git clone <repository-url>
cd project.quizly.backend
```

2. **Create virtual environment**
```bash
python -m venv env
# Windows
.\env\Scripts\Activate.ps1
# Linux/Mac
source env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy .env.example to .env
cp .env.example .env
# Add API keys to .env
```

5. **Migrate database**
```bash
python manage.py migrate
```

6. **Run tests**
```bash
python manage.py test
```

7. **Start development server**
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register user
- `POST /api/auth/login/` - Login (sets JWT cookies)
- `POST /api/auth/logout/` - Logout (requires auth)
- `POST /api/auth/token/refresh/` - Refresh token

### Quizzes
- `POST /api/quizzes/create-from-youtube/` - Create quiz from YouTube video
- More endpoints see `quizzes_app/api/urls.py`

## Configuration

### Important Settings in `core/settings.py`:

```python
# JWT Token Lifetime
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Cookie Names (used by middleware)
# - 'access' for Access Token
# - 'refresh' for Refresh Token
```

### Production Notes

- Set `DEBUG = False`
- Change `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Set webserver timeout to 300s+ for long video processing
- Install FFmpeg in system PATH

## Project Structure

```
project.quizly.backend/
├── auth_app/           # Authentication & User Management
│   ├── api/           # API Views & Serializers
│   ├── tests/         # Unit Tests
│   └── middleware.py  # JWT Cookie Middleware
├── quizzes_app/       # Quiz Functionality
│   └── api/           # YouTube & Quiz Generation
├── core/              # Django Settings & URLs
├── media/             # Temporary Audio Files
└── requirements.txt   # Python Dependencies
```

## Tests

```bash
# All tests
python manage.py test

# Only auth tests
python manage.py test auth_app.tests

# Single test
python manage.py test auth_app.tests.test_login_logout.LoginLogoutTests.test_login
```

## Troubleshooting

### FFmpeg not found
```
Error: ffmpeg not found
```
**Solution:** Install FFmpeg or set `FFMPEG_PATH` in `.env`

### No Whisper models
```
Error: Model 'turbo' not found
```
**Solution:** On first run, Whisper automatically downloads the model (~1.5GB)

### Token errors
```
Error: Refresh token not found
```
**Solution:** Make sure the middleware is enabled in `settings.MIDDLEWARE`

## License

MIT License

## Support

For questions or issues, please create an issue.
