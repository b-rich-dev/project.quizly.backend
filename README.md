# Quizly Backend

Django REST API Backend for the Quizly application with YouTube video integration and AI-powered quiz generation.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [FFmpeg Installation](#ffmpeg-installation)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Admin Panel](#admin-panel)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration Details](#configuration-details)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- 🔐 **JWT Authentication** with HTTP-only cookies
- 👤 **User Management** (Registration, Login, Logout, Token Refresh)
- 📹 **YouTube Integration** - Download and process YouTube videos
- 🎤 **Audio Transcription** - Powered by OpenAI Whisper
- 🤖 **AI Quiz Generation** - Automatic quiz creation with Google Gemini
- 📝 **Quiz Management** - Create, read, update, delete quizzes
- 🔒 **Permission System** - User-specific quiz access
- ✅ **Comprehensive Testing** - Full test coverage for all features
- 👨‍💼 **Admin Panel** - Django admin interface for user and quiz management

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **FFmpeg** (required for audio/video processing)
- **Google Gemini API Key** ([Get API Key](https://ai.google.dev/))
- **Git** (for cloning the repository)

### Why FFmpeg is Required

FFmpeg is essential for:
- Extracting audio from YouTube videos
- Converting video/audio formats
- Processing media files for transcription

Without FFmpeg, the YouTube video processing will **not work**.

## 🎬 FFmpeg Installation

### Windows

**Option 1: Using Winget (Recommended)**
```powershell
winget install Gyan.FFmpeg
```

**Option 2: Manual Installation**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the archive (e.g., to `C:\ffmpeg`)
3. Add FFmpeg to your system PATH:
   - Open "Environment Variables"
   - Add `C:\ffmpeg\bin` to the PATH variable
4. Verify installation:
```powershell
ffmpeg -version
```

**Option 3: Using Chocolatey**
```powershell
choco install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### macOS

**Using Homebrew:**
```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### FFmpeg PATH Configuration

- **If FFmpeg is in system PATH:** No additional configuration needed
- **If FFmpeg is NOT in PATH:** Set `FFMPEG_PATH` in your `.env` file:
  ```env
  # Windows
  FFMPEG_PATH=C:\ffmpeg\bin
  
  # Linux/Mac
  FFMPEG_PATH=/usr/local/bin/ffmpeg
  ```

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/b-rich-dev/project.quizly.backend
cd project.quizly.backend
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** On first run, Whisper will automatically download the `base` model (~150 MB). This is a one-time download.

### 4. Create Environment File

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your configuration (see [Environment Configuration](#environment-configuration))

## ⚙️ Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Gemini API Key (REQUIRED)
# Get your API key from: https://ai.google.dev/
GEMINI_API_KEY=your-gemini-api-key-here

# FFmpeg Path (OPTIONAL)
# Only needed if FFmpeg is not in your system PATH
# Windows example: FFMPEG_PATH=C:\ffmpeg\bin
# Linux/Mac example: FFMPEG_PATH=/usr/local/bin/ffmpeg
# Leave empty or comment out if FFmpeg is already in PATH
# FFMPEG_PATH=
```

**Note:** `SECRET_KEY` and `DEBUG` are configured directly in `core/settings.py`. For production deployment, you must update these values in the settings file (see [Production Deployment](#production-deployment)).

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key to your `.env` file

## 🗄️ Database Setup

The project uses SQLite by default (no additional setup required).

### Run Migrations

```bash
python manage.py migrate
```

### Create Superuser (for Admin Panel)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## ▶️ Running the Application

### Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

### Run in Background (Optional)

**Windows:**
```powershell
Start-Process python -ArgumentList "manage.py runserver" -NoNewWindow
```

**Linux/macOS:**
```bash
nohup python manage.py runserver &
```

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication Endpoints

#### Register User
```http
POST /api/register/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_confirmed_password",
  "email": "your_email@example.com"
}
```

**Response (201 Created):**
```json
{
  "detail": "User created successfully."
}
```

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200 OK):**
```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

**Cookies set:** `access`, `refresh`

#### Logout
```http
POST /api/logout/
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

#### Refresh Token
```http
POST /api/token/refresh/
Cookie: refresh=<refresh_token>
```

**Response (200 OK):**
```json
{
  "detail": "Token refreshed"
}
```

**Cookie updated:** `access`

### Quiz Endpoints

#### Get User's Quizzes
```http
GET /api/quizzes/
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Python Basics",
    "description": "Learn Python fundamentals",
    "created_at": "2023-07-29T12:34:56.789Z",
    "updated_at": "2023-07-29T12:34:56.789Z",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": [
      {
        "id": 1,
        "question_title": "Question 1",
        "question_options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "answer": "Option A"
      }
    ]
  }
]
```

#### Create Quiz from YouTube
```http
POST /api/quizzes/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A",
      "created_at": "2023-07-29T12:34:56.789Z",
      "updated_at": "2023-07-29T12:34:56.789Z"
    }
  ]
}
```

**Note:** This operation can take 30-60 seconds depending on video length.

#### Get Single Quiz
```http
GET /api/quizzes/{id}/
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A"
    }
  ]
}
```

#### Update Quiz
```http
PUT /api/quizzes/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated Description"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Title",
  "description": "Updated Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T14:45:12.345Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A"
    }
  ]
}
```

#### Partial Update Quiz
```http
PATCH /api/quizzes/{id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Partially Updated Title"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Partially Updated Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T14:45:12.345Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A"
    }
  ]
}
```

#### Delete Quiz
```http
DELETE /api/quizzes/{id}/
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

## 👨‍💼 Admin Panel

Access the Django admin interface at: `http://127.0.0.1:8000/admin/`

### Features:
- **User Management** - View, edit, create users with enhanced display
- **Quiz Management** - Inline editing of quizzes and questions
- **Question Management** - Standalone question editing
- **Filtering & Search** - Advanced filtering options
- **Timestamps** - Track creation and update times

### Login:
Use the superuser credentials you created during setup.

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Suites

**Authentication Tests:**
```bash
python manage.py test auth_app.tests
```

**Quiz Tests:**
```bash
python manage.py test quizzes_app.tests
```

### Run Specific Test Class
```bash
python manage.py test auth_app.tests.test_login_logout.LoginLogoutTests
```

### Run Single Test
```bash
python manage.py test auth_app.tests.test_login_logout.LoginLogoutTests.test_login
```

### Test Coverage

- ✅ User registration with validation
- ✅ Login/Logout with JWT cookies
- ✅ Token refresh and blacklisting
- ✅ Quiz creation from YouTube videos (mocked)
- ✅ Quiz CRUD operations
- ✅ Permission-based access control
- ✅ Error handling and edge cases

## 📁 Project Structure

```
project.quizly.backend/
├── auth_app/                   # Authentication & User Management
│   ├── api/
│   │   ├── serializers.py     # User & Token serializers
│   │   ├── views.py           # Auth endpoints
│   │   └── urls.py            # Auth routes
│   ├── tests/
│   │   ├── test_registration.py
│   │   └── test_login_logout.py
│   ├── admin.py               # Custom User admin
│   └── middleware.py          # JWT Cookie middleware
│
├── quizzes_app/               # Quiz Management
│   ├── api/
│   │   ├── serializers.py     # Quiz & Question serializers
│   │   ├── views.py           # Quiz endpoints
│   │   ├── permissions.py     # Custom permissions
│   │   ├── utils.py           # YouTube, Whisper, Gemini utilities
│   │   └── urls.py            # Quiz routes
│   ├── tests/
│   │   ├── test_api.py        # Quiz API tests
│   │   └── test_quiz_detail.py
│   ├── models.py              # Quiz & Question models
│   └── admin.py               # Quiz admin with inline editing
│
├── core/                      # Django Project Settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py                # WSGI config
│   └── asgi.py                # ASGI config
│
├── media/                     # Temporary audio files
├── db.sqlite3                 # SQLite database
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                  # This file
```

## 🔧 Configuration Details

### JWT Settings (`core/settings.py`)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

- **Access Token:** Valid for 5 minutes
- **Refresh Token:** Valid for 1 day
- **Token Rotation:** Enabled (new refresh token on each refresh)
- **Blacklisting:** Old tokens are blacklisted after logout

### CORS Settings

```python
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5500',
    'http://localhost:5500',
]

CORS_ALLOW_CREDENTIALS = True
```

**For production:** Update `CORS_ALLOWED_ORIGINS` with your frontend URL.

### Cookie Configuration

JWT tokens are stored as HTTP-only cookies:
- `access` - Access token cookie
- `refresh` - Refresh token cookie
- `httponly=True` - Not accessible via JavaScript
- `secure=True` - HTTPS only (for production)
- `samesite='Lax'` - CSRF protection

### Whisper Model

The project uses Whisper's `base` model (~150 MB):
- Good balance between speed and accuracy
- Supports 99 languages
- Downloads automatically on first use

To change the model, edit `quizzes_app/api/utils.py`:
```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

## 🌐 Production Deployment

### Pre-deployment Checklist

1. **Update Settings in `core/settings.py`:**
   ```python
   # CRITICAL: Change these values before deploying to production
   SECRET_KEY = '<generate-strong-secret-key>'  # Generate a new secret key
   DEBUG = False  # MUST be False in production
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

2. **Environment Variables (.env file):**
   ```env
   GEMINI_API_KEY=<your-api-key>
   # FFMPEG_PATH=<path-if-needed>
   ```

3. **Security Settings (add to `core/settings.py`):**
   ```python
   # Update existing settings
   CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
   CORS_ALLOWED_ORIGINS = ['https://your-frontend.com']
   
   # Add for HTTPS
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

4. **Web Server Configuration:**
   - **Timeout:** Set to 300+ seconds (YouTube processing can be slow)
   - **Gunicorn example:**
     ```bash
     gunicorn core.wsgi:application --timeout 300 --workers 4
     ```

5. **Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Database:**
   - Consider PostgreSQL for production
   - Update `DATABASES` in `settings.py`

7. **FFmpeg:**
   - Ensure FFmpeg is installed on production server
   - Add to system PATH or set `FFMPEG_PATH` in `.env`

8. **Media Files:**
   - Configure proper storage for `media/` directory
   - Consider cleanup job for temporary audio files

### Recommended Stack

- **Web Server:** Nginx
- **WSGI Server:** Gunicorn
- **Database:** PostgreSQL
- **OS:** Ubuntu/Debian Linux

## 🐛 Troubleshooting

### FFmpeg Not Found

```
Error: ffmpeg not found in PATH
```

**Solutions:**
1. Install FFmpeg (see [FFmpeg Installation](#ffmpeg-installation))
2. Verify installation: `ffmpeg -version`
3. If installed but not in PATH, set `FFMPEG_PATH` in `.env`

### Whisper Model Download Issues

```
Error: Model 'base' not found
```

**Solution:** On first run, Whisper downloads the model (~150 MB). Ensure:
- Stable internet connection
- Sufficient disk space (~500 MB recommended)
- Write permissions in home directory

**Manual download location:** `~/.cache/whisper/`

### Gemini API Errors

```
ValueError: GEMINI_API_KEY environment variable is not set
```

**Solution:**
1. Get API key from [Google AI Studio](https://ai.google.dev/)
2. Add to `.env` file: `GEMINI_API_KEY=your-key-here`
3. Restart the server

```
Error: Quota exceeded
```

**Solution:** Gemini free tier has usage limits. Check your quota at [Google AI Studio](https://aistudio.google.com/).

### Token/Authentication Issues

```
Error: Refresh token not found
```

**Solution:**
- Ensure `JWTAuthCookieMiddleware` is in `MIDDLEWARE` (check `settings.py`)
- Check that cookies are being set correctly
- Verify CORS settings allow credentials

```
401 Unauthorized
```

**Solution:**
- Access token expired (valid for 5 minutes)
- Use refresh token endpoint to get new access token
- Check that `Authorization: Bearer <token>` header is set correctly

### YouTube Download Errors

```
YouTubeDownloadError: Video not available
```

**Solutions:**
- Verify YouTube URL is correct
- Video might be private, age-restricted, or region-blocked
- Check internet connection
- Update `yt-dlp`: `pip install --upgrade yt-dlp`

### Database Issues

```
Error: no such table
```

**Solution:**
```bash
python manage.py migrate
```

### Port Already in Use

```
Error: That port is already in use
```

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001
```

## 📝 Dependencies

Key dependencies from `requirements.txt`:

- **Django 6.0.2** - Web framework
- **djangorestframework 3.16.1** - REST API
- **djangorestframework-simplejwt 5.5.1** - JWT authentication
- **openai-whisper 20250625** - Audio transcription
- **google-genai 1.64.0** - Quiz generation
- **yt-dlp** - YouTube downloader
- **python-dotenv 1.2.1** - Environment variables

## 📄 License

MIT License

## 🤝 Support

For questions, issues, or contributions:
- Check documentation
- Create an issue on GitHub
- Contact the developer: info@birich.it

## 🔄 Updates

Keep dependencies updated regularly:
```bash
pip install --upgrade -r requirements.txt
```

---

**Built with ❤️ using Django, Whisper AI, and Google Gemini**
