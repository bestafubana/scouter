# Scouter - Receipt Processing System

Scouter is a standalone receipt processing system with magic link authentication, database-backed user management, and AI-powered data extraction.

## Table of Contents

- [Scouter - Receipt Processing System](#scouter---receipt-processing-system)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [1. Setup Environment](#1-setup-environment)
    - [2. Start MailHog (Email Testing)](#2-start-mailhog-email-testing)
    - [3. Start Scouter](#3-start-scouter)
    - [4. Access Scouter](#4-access-scouter)
    - [5. Login Process](#5-login-process)
      - [For Existing Users:](#for-existing-users)
      - [For New Users (First Time):](#for-new-users-first-time)
  - [Test Users](#test-users)
    - [Acme Corporation](#acme-corporation)
    - [Tech Innovations Inc](#tech-innovations-inc)
    - [Green Energy Solutions](#green-energy-solutions)
    - [Testing New User Registration](#testing-new-user-registration)
  - [Development Setup](#development-setup)
    - [Email Testing with MailHog](#email-testing-with-mailhog)
    - [Database Management](#database-management)
  - [API Documentation](#api-documentation)
  - [API Endpoints](#api-endpoints)
    - [Authentication Endpoints](#authentication-endpoints)
    - [Frontend Endpoints](#frontend-endpoints)
  - [Email Configuration](#email-configuration)
    - [Development (MailHog)](#development-mailhog)
    - [Production (Amazon SES)](#production-amazon-ses)
  - [Database Configuration](#database-configuration)
    - [Development (SQLite)](#development-sqlite)
    - [Production (PostgreSQL)](#production-postgresql)
  - [Security Features](#security-features)
  - [File Structure](#file-structure)
  - [Troubleshooting](#troubleshooting)
    - [Email Issues](#email-issues)
    - [Database Issues](#database-issues)
    - [Server Issues](#server-issues)
    - [Health Check](#health-check)
  - [Production Deployment](#production-deployment)
    - [Environment Variables](#environment-variables)
    - [Deployment Checklist](#deployment-checklist)

## Features

- 🔐 **Magic Link Authentication** - Passwordless login via email
- 📧 **MailHog Email Testing** - Visual email testing for development  
- 👥 **Multi-Organization Support** - Users belong to organizations
- 👑 **Admin Panel** - User management for administrators
- 👨‍💼 **Manager System** - Organization managers can invite new team members
- 💾 **Database-Backed** - SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- 🔄 **Database Migrations** - Flask-Migrate for schema management
- 📱 **Mobile-Friendly** - Responsive authentication UI
- 🏥 **Health Monitoring** - Beautiful health check dashboard (admin only)

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
export FLASK_APP=auth_server.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed test data
python seed_data.py
```

### 2. Start MailHog (Email Testing)

```bash
# Install MailHog (macOS)
brew install mailhog

# Start MailHog
mailhog &
```

**📧 MailHog URLs:**
- **Email Inbox**: http://localhost:8025 (view sent emails)
- **SMTP Server**: localhost:1025 (for sending emails)

### 3. Start Scouter

```bash
./start.sh
```

The server will start on `http://localhost:5001` (or `http://localhost:5000` if 5001 is busy)

### 4. Access Scouter

Open your browser and go to:
```
http://localhost:5001/
```

### 5. Login Process

#### For Existing Users:
1. Click the **🔐 Login** button in the top-right corner
2. Enter a test user email (see test users below)
3. Click **✨ Send Magic Link**
4. **Check MailHog at http://localhost:8025** to see the email
5. Click the magic link in the email to authenticate
6. You'll be logged in with your name and organization displayed

#### For New Users (First Time):
1. Click the **🔐 Login** button in the top-right corner
2. Enter any new email address (not in test users list)
3. Click **✨ Send Magic Link**
4. **Check MailHog at http://localhost:8025** to see the email
5. Click the magic link in the email
6. **Registration Modal appears** - Enter your name and organization
7. Click **🚀 Complete Registration**
8. You'll be registered and logged in automatically

## Test Users

The system comes pre-seeded with test users across different organizations:

### Acme Corporation
- `john.doe@acme.com` - John Doe
- `jane.smith@acme.com` - Jane Smith

### Tech Innovations Inc  
- `alice.johnson@techinnovations.com` - Alice Johnson
- `bob.wilson@techinnovations.com` - Bob Wilson

### Green Energy Solutions
- `carol.davis@greenenergy.com` - Carol Davis
- `david.brown@greenenergy.com` - David Brown

### Testing New User Registration

To test the new user registration flow, use any email that's **not** in the list above, such as:
- `newuser@example.com`
- `test@mycompany.com`
- `your.email@domain.com`

These will trigger the registration modal where you can create a new organization and user account.

## Development Setup

### Email Testing with MailHog

MailHog captures all emails sent by the application, allowing you to:

- ✅ **See actual HTML emails** with full styling
- ✅ **Test magic link functionality** end-to-end
- ✅ **Debug email issues** without sending real emails
- ✅ **View email content** in a web interface

**Important URLs:**
- **MailHog Web UI**: http://localhost:8025 (check emails here!)
- **Scouter App**: http://localhost:5001/
- **Health Check**: http://localhost:5001/health (no login required in dev mode)
- **API Documentation**: http://localhost:5001/api/docs
- **Admin Panel**: http://localhost:5001/admin/users (no login required in dev mode)

### Development Mode

Scouter runs in development mode by default (`DEV_MODE = True` in `auth_server.py`). In development mode:

- 🔓 **Admin pages unlocked** - No authentication required for `/health` and `/admin/users`
- ⚠️ **Development banners** - Yellow warning banners indicate when auth is disabled
- 📧 **MailHog integration** - Email testing with local SMTP server
- 🔍 **Debug information** - Additional logging and error details

**Production Deployment:**
Set `DEV_MODE = False` in `auth_server.py` to enable full authentication requirements.

### Database Management

```bash
# Create new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Reset database (development only)
rm scouter.db
flask db upgrade
python seed_data.py
```

## API Documentation

Scouter provides comprehensive API documentation using Redocly. The interactive documentation includes:

- 📚 **Complete API Reference** - All endpoints with detailed descriptions
- 🔍 **Interactive Examples** - Try API calls directly from the documentation
- 📝 **Request/Response Schemas** - Detailed data models and examples
- 🔐 **Authentication Guide** - How to use magic link authentication

**Access the API Documentation:**
- **Interactive Docs**: http://localhost:5001/api/docs
- **OpenAPI Spec**: http://localhost:5001/api/openapi.yaml

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/send-magic-link` | POST | Send magic link to email (works for new and existing users) |
| `/api/auth/verify` | POST | Verify magic token (returns registration prompt for new users) |
| `/api/auth/register` | POST | Complete new user registration |
| `/api/auth/invite` | POST | Invite new team member (manager only) |
| `/api/auth/status` | GET | Check authentication status |
| `/api/auth/logout` | POST | Logout user |
| `/api/health` | GET | Health check (JSON) |

### Frontend Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main Scouter interface (redirects to index.html) |
| `/index.html` | Scouter application |
| `/health` | Health check dashboard (HTML) |

## Email Configuration

### Development (MailHog)

```python
# Current development settings in auth_server.py
MAIL_SERVER = 'localhost'
MAIL_PORT = 1025
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEFAULT_SENDER = 'noreply@scouter.local'
```

### Production (Amazon SES)

For production, update email configuration:

```python
# Production settings for Amazon SES
MAIL_SERVER = 'email-smtp.us-east-1.amazonaws.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv('AWS_SES_USERNAME')
MAIL_PASSWORD = os.getenv('AWS_SES_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('FROM_EMAIL', 'noreply@yourdomain.com')
```

**Environment Variables for Production:**
```bash
AWS_SES_USERNAME=your_ses_username
AWS_SES_PASSWORD=your_ses_password
FROM_EMAIL=noreply@yourdomain.com
```

## Database Configuration

### Development (SQLite)
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///scouter.db'
```

### Production (PostgreSQL)
```python
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/scouter')
```

## Security Features

- 🔒 **Secure Token Generation** - Uses `secrets.token_urlsafe(32)`
- ⏰ **Token Expiration** - Magic links expire in 15 minutes
- 🎫 **One-Time Use** - Tokens can only be used once
- 🧹 **Automatic Cleanup** - Expired tokens are automatically removed
- 👤 **User Validation** - Only registered users can authenticate
- 🏢 **Organization Isolation** - Users belong to specific organizations

## File Structure

```
scouter/
├── auth_server.py              # Main authentication server
├── models.py                   # SQLAlchemy database models
├── index.html                  # Frontend application
├── requirements.txt            # Python dependencies
├── start.sh                    # Startup script with port management
├── seed_data.py               # Database seeding script
├── test_email.py              # Email testing script
├── migrations/                 # Database migration files
├── scouter.db                 # SQLite database (development)
└── README.md                  # This documentation
```

## Troubleshooting

### Email Issues

**Magic links not being sent:**
1. Check if MailHog is running: `ps aux | grep mailhog`
2. Start MailHog: `mailhog &`
3. Check MailHog UI: http://localhost:8025
4. Verify user exists in database with correct email

**MailHog not working:**
```bash
# Install MailHog
brew install mailhog

# Start MailHog manually
mailhog

# Check if ports are available
lsof -i :1025  # SMTP port
lsof -i :8025  # Web UI port
```

### Database Issues

**Migration errors:**
```bash
# Reset migrations (development only)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**User not found errors:**
```bash
# Re-seed the database
python seed_data.py
```

### Server Issues

**Port conflicts:**
- The start script automatically switches to port 5001 if 5000 is busy
- Check running processes: `lsof -i :5000` or `lsof -i :5001`

### Health Check

Monitor the system status:
```bash
curl http://localhost:5001/api/health
```

Or visit the beautiful dashboard: http://localhost:5001/health

## Production Deployment

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/scouter

# Email (Amazon SES)
AWS_SES_USERNAME=your_ses_username
AWS_SES_PASSWORD=your_ses_password
FROM_EMAIL=noreply@yourdomain.com

# Security
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

### Deployment Checklist

**Database:**
- [ ] Set up PostgreSQL database
- [ ] Run migrations: `flask db upgrade`
- [ ] Create production users (don't use seed data)

**Email:**
- [ ] Configure Amazon SES credentials
- [ ] Verify sender email domain
- [ ] Update email templates with production branding

**Security:**
- [ ] Set strong SECRET_KEY
- [ ] Configure proper CORS settings
- [ ] Add rate limiting
- [ ] Set up HTTPS/SSL
- [ ] Implement session timeout

**Infrastructure:**
- [ ] Set up monitoring and logging
- [ ] Configure backup strategies
- [ ] Set up CI/CD pipeline

---

**Ready for development!** Start MailHog, run `./start.sh`, and visit http://localhost:8025 to see emails. 