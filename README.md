# Scouter - Receipt Processing System

Scouter is a standalone receipt processing system with magic link authentication, database-backed user management, and AI-powered data extraction.

## Table of Contents

- [Scouter - Receipt Processing System](#scouter---receipt-processing-system)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Quick Start](#quick-start)
    - [1. Setup Environment](#1-setup-environment)
    - [2. Setup Google Cloud (Optional)](#2-setup-google-cloud-optional)
      - [**Step-by-Step Google Cloud Setup:**](#step-by-step-google-cloud-setup)
      - [**Authentication Methods:**](#authentication-methods)
    - [3. Start MailHog (Email Testing)](#3-start-mailhog-email-testing)
    - [4. Start Scouter](#4-start-scouter)
    - [5. Access Scouter](#5-access-scouter)
    - [6. Login Process](#6-login-process)
      - [For Existing Users:](#for-existing-users)
      - [For New Users (First Time):](#for-new-users-first-time)
  - [Test Users](#test-users)
    - [Acme Corporation](#acme-corporation)
    - [Tech Innovations Inc](#tech-innovations-inc)
    - [Green Energy Solutions](#green-energy-solutions)
    - [Testing New User Registration](#testing-new-user-registration)
  - [Development Setup](#development-setup)
    - [Email Testing with MailHog](#email-testing-with-mailhog)
    - [Development Mode](#development-mode)
    - [Database Management](#database-management)
  - [Development Guidelines](#development-guidelines)
    - [⚠️ Critical: Always Check Existing Infrastructure First](#️-critical-always-check-existing-infrastructure-first)
    - [🚫 Common Mistakes to Avoid](#-common-mistakes-to-avoid)
      - [**DO NOT use localStorage for data that belongs in the database**](#do-not-use-localstorage-for-data-that-belongs-in-the-database)
      - [**DO NOT ignore existing authentication system**](#do-not-ignore-existing-authentication-system)
      - [**DO NOT bypass user/organization tracking**](#do-not-bypass-userorganization-tracking)
    - [🎯 Best Practices](#-best-practices)
      - [**1. User and Receipt Management**](#1-user-and-receipt-management)
      - [**2. Authentication Flow**](#2-authentication-flow)
      - [**3. Frontend Development**](#3-frontend-development)
      - [**4. API Development**](#4-api-development)
      - [**5. Generic Naming Convention**](#5-generic-naming-convention)
    - [📚 Key Files Reference](#-key-files-reference)
    - [🔍 Quick Checklist Before Coding](#-quick-checklist-before-coding)
  - [Receipt Processing Pipeline](#receipt-processing-pipeline)
    - [🔄 Processing Flow](#-processing-flow)
      - [Processing Steps:](#processing-steps)
    - [📊 Real-time Progress](#-real-time-progress)
    - [🎯 Key Features](#-key-features)
    - [📋 Receipt Record Lifecycle](#-receipt-record-lifecycle)
      - [1. **Create Receipt Record** (Before Upload)](#1-create-receipt-record-before-upload)
      - [2. **Upload Image to S3**](#2-upload-image-to-s3)
      - [3. **Run OCR** (Google Document AI)](#3-run-ocr-google-document-ai)
      - [4. **Extract Structured Fields** (via GPT)](#4-extract-structured-fields-via-gpt)
      - [5. **Update Key Fields from AI Output**](#5-update-key-fields-from-ai-output)
      - [6. **Finalize / Ready for Review**](#6-finalize--ready-for-review)
      - [Status Values:](#status-values)
    - [🔧 Configuration](#-configuration)
      - [🔑 **AWS S3 Configuration**](#-aws-s3-configuration)
      - [🤖 **OpenAI Configuration**](#-openai-configuration)
      - [🔍 **Google Document AI Configuration**](#-google-document-ai-configuration)
      - [⚙️ **Processing Settings**](#️-processing-settings)
  - [API Documentation](#api-documentation)
  - [API Endpoints](#api-endpoints)
    - [Authentication Endpoints](#authentication-endpoints)
    - [Receipt Processing Endpoints](#receipt-processing-endpoints)
      - [GET `/api/receipts`](#get-apireceipts)
      - [POST `/api/receipt/verify`](#post-apireceiptverify)
    - [Frontend Endpoints](#frontend-endpoints)
  - [Email Configuration](#email-configuration)
    - [Development (MailHog)](#development-mailhog)
    - [Production (Amazon SES)](#production-amazon-ses)
  - [Database Configuration](#database-configuration)
    - [Development (SQLite)](#development-sqlite)
    - [Production (PostgreSQL)](#production-postgresql)
  - [Security Features](#security-features)
  - [File Structure](#file-structure)
  - [Performance Monitoring with Prometheus \& Grafana](#performance-monitoring-with-prometheus--grafana)
    - [📊 Available Metrics](#-available-metrics)
      - [**Overall Pipeline Metrics**](#overall-pipeline-metrics)
      - [**Per-Step Performance**](#per-step-performance)
      - [**Quality Metrics**](#quality-metrics)
      - [**Cost Tracking**](#cost-tracking)
      - [**Additional Metrics**](#additional-metrics)
    - [🚀 Quick Start with Prometheus](#-quick-start-with-prometheus)
    - [📈 Quick Start with Grafana](#-quick-start-with-grafana)
    - [📊 Sample Grafana Dashboard JSON](#-sample-grafana-dashboard-json)
    - [🔍 Useful Prometheus Queries](#-useful-prometheus-queries)
    - [🎯 Recommended Alerts](#-recommended-alerts)
    - [📝 Testing Metrics](#-testing-metrics)
    - [🎨 Grafana Dashboard Tips](#-grafana-dashboard-tips)
  - [Troubleshooting](#troubleshooting)
    - [Email Issues](#email-issues)
    - [Database Issues](#database-issues)
    - [Server Issues](#server-issues)
    - [Health Check](#health-check)
    - [Google Document AI Issues](#google-document-ai-issues)
  - [Production Deployment](#production-deployment)
    - [AWS Deployment (Recommended)](#aws-deployment-recommended)
      - [🔐 **Google Cloud Credentials on AWS**](#-google-cloud-credentials-on-aws)
      - [🚀 **AWS Deployment Options**](#-aws-deployment-options)
      - [🔒 **Security Best Practices for AWS**](#-security-best-practices-for-aws)
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
- 📄 **Enhanced Receipt Processing** - Real-time processing pipeline with visual progress
- ☁️ **S3 Integration** - Secure cloud storage for receipt images
- 🔍 **Tesseract OCR** - Advanced text extraction from receipt images
- 🤖 **OpenAI Integration** - AI-powered data structuring with confidence scoring
- 📊 **Real-time Progress** - Live updates with Alpine.js-powered flow visualization

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy template and edit with your API keys)
cp env_template.txt .env
# Edit .env with your AWS S3 and OpenAI API keys (optional for development)

# Initialize database
export FLASK_APP=auth_server.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed test data
python seed_data.py
```

### 2. Setup Google Cloud (Optional)

For real Document AI processing (otherwise uses mock mode):

#### **Step-by-Step Google Cloud Setup:**

1. **Create Google Cloud Project**
   ```bash
   # Go to https://console.cloud.google.com/
   # Create new project or select existing one
   ```

2. **Enable Document AI API**
   ```bash
   # In Google Cloud Console:
   # APIs & Services → Library → Search "Document AI API" → Enable
   ```

3. **Create Document AI Processor**
   ```bash
   # Document AI → Processors → Create Processor
   # Choose "Invoice Parser" or "Form Parser" for receipts
   # Note the Processor ID (long string like "abc123def456...")
   ```

4. **Create Service Account & Download Credentials**
   ```bash
   # IAM & Admin → Service Accounts → Create Service Account
   # Grant role: "Document AI API User"
   # Create Key → JSON → Download the .json file
   ```

5. **Update Environment Configuration**
   ```bash
   # Add to .env file:
   GOOGLE_CLOUD_PROJECT_ID=your-project-id
   GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your-processor-id
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

6. **Test Your Setup**
   ```bash
   # Run the authentication test script
   python test_google_auth.py
   ```
   This script will verify all your credentials and configuration.

#### **Authentication Methods:**

- **Local Development**: Service Account JSON key file
- **AWS Production**: Service Account JSON key file (secure storage)
- **GCP Production**: Workload Identity, Instance Service Account
- **Local Testing Alternative**: `gcloud auth application-default login`

See [Google Document AI Setup Guide](https://cloud.google.com/document-ai/docs/setup) for detailed instructions.

### 3. Start MailHog (Email Testing)

```bash
# Install MailHog (macOS)
brew install mailhog

# Start MailHog
mailhog &
```

**📧 MailHog URLs:**
- **Email Inbox**: http://localhost:8025 (view sent emails)
- **SMTP Server**: localhost:1025 (for sending emails)

### 4. Start Scouter

```bash
./start.sh
```

The server will start on `http://localhost:5001` (or `http://localhost:5000` if 5001 is busy)

### 5. Access Scouter

Open your browser and go to:
```
http://localhost:5001/
```

### 6. Login Process

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

## Development Guidelines

### ⚠️ Critical: Always Check Existing Infrastructure First

**Before implementing ANY new feature, ALWAYS check if infrastructure already exists:**

1. **Check `models.py`** - Look for existing database models before creating new ones
2. **Check `auth_server.py`** - Look for existing API endpoints before creating new ones
3. **Check `README.md`** - Review architecture and existing features
4. **Use existing patterns** - Follow the established code structure

### 🚫 Common Mistakes to Avoid

#### **DO NOT use localStorage for data that belongs in the database**

❌ **Wrong:**
```javascript
// Storing receipts in localStorage
localStorage.setItem('receipts', JSON.stringify(receipts));
```

✅ **Correct:**
```javascript
// Use existing API and database
const response = await fetch('/api/receipts');
const data = await response.json();
```

**Why:** Scouter has a complete database system with SQLAlchemy models. Always use:
- Database models (in `models.py`)
- API endpoints (in `auth_server.py`)
- Proper authentication and user tracking

#### **DO NOT ignore existing authentication system**

❌ **Wrong:**
```python
# Creating custom session management
user_id = request.headers.get('user-id')
```

✅ **Correct:**
```python
# Use Flask session (configured in auth_server.py)
user_id = session.get('user_id')
if not user_id:
    return jsonify({'error': 'Not authenticated'}), 401
```

#### **DO NOT bypass user/organization tracking**

❌ **Wrong:**
```python
# Using test data for all users
user_id = 'test@example.com'
```

✅ **Correct:**
```python
# Use authenticated user's UUID
user_id = session.get('user_id')
user = User.query.filter_by(uuid=user_id).first()
# Save with user.uuid for proper multi-tenant support
```

### 🎯 Best Practices

#### **1. User and Receipt Management**

- **Users are identified by UUID** (not integer ID)
- **Receipts belong to users** via `user_id` (UUID foreign key)
- **Organizations are tracked** via `org_id` in User model
- **Always filter by authenticated user** when querying receipts

```python
# Correct way to get user's receipts
user_id = session.get('user_id')
receipts = Receipt.query.filter_by(
    user_id=user_id,
    is_deleted=False
).order_by(Receipt.created_at.desc()).all()
```

#### **2. Authentication Flow**

- **Session storage:** Flask session stores `user_id` (UUID)
- **Dual storage:** Also stored in `authenticated_users` dict for Bearer token support
- **SECRET_KEY required:** Flask session needs `app.config['SECRET_KEY']`
- **Both login and registration** must set session data

```python
# Correct authentication setup
session['user_id'] = user.uuid
session['email'] = user.email
session['name'] = user.name
```

#### **3. Frontend Development**

- **Use existing Scouter class** - Don't create parallel state management
- **Alpine.js for reactivity** - Already integrated for progress tracking
- **Client-side filtering** - Filter/paginate data received from API
- **Respect existing DOM structure** - Don't arbitrarily move elements (breaks Alpine.js)

```javascript
// Correct: Store all data, filter client-side
this.allReceipts = data.receipts;
this.filteredReceipts = this.allReceipts.filter(/* filters */);
```

#### **4. API Development**

- **Check for existing endpoints** before creating new ones
- **Use consistent patterns** with existing API structure
- **Return proper error codes** (401 for auth, 404 for not found, etc.)
- **Include authentication checks** on all protected endpoints

```python
# Standard API pattern
@app.route('/api/receipts', methods=['GET'])
def list_receipts():
    # 1. Check authentication
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # 2. Query database with user filter
    receipts = Receipt.query.filter_by(
        user_id=user_id,
        is_deleted=False
    ).all()
    
    # 3. Return structured response
    return jsonify({
        'receipts': [r.to_dict() for r in receipts],
        'total': len(receipts)
    })
```

#### **5. Generic Naming Convention**

**DO NOT expose internal technology stack in user-facing text:**

❌ **Avoid:** "S3 Upload Failed", "Google Document AI Error", "GPT Processing"

✅ **Use:** "Image Upload Failed", "Image Recognition Error", "AI Analysis"

**Why:** Technology choices may change, and users don't need to know implementation details.

### 📚 Key Files Reference

| File | Purpose | When to Check |
|------|---------|--------------|
| `models.py` | Database models (User, Receipt, Organization) | Before adding any data storage |
| `auth_server.py` | API endpoints and authentication | Before adding any API routes |
| `index.html` | Frontend application (Scouter class) | Before adding UI features |
| `README.md` | Architecture and API docs | Start here for any feature |
| `seed_data.py` | Test data structure | To understand data relationships |

### 🔍 Quick Checklist Before Coding

- [ ] Read relevant sections of README.md
- [ ] Check if database model exists in models.py
- [ ] Check if API endpoint exists in auth_server.py
- [ ] Review existing frontend patterns in index.html
- [ ] Verify authentication is properly implemented
- [ ] Use UUIDs (not integer IDs) for user references
- [ ] Filter data by authenticated user
- [ ] Use generic terminology (not AWS/Google/OpenAI)
- [ ] Test with actual user login flow

## Receipt Processing Pipeline

Scouter features an advanced receipt processing system with real-time progress tracking:

### 🔄 Processing Flow

```mermaid
sequenceDiagram
  User->>Backend: Upload receipt
  Backend->>DB: Create empty receipt
  Backend->>S3: Upload file
  Backend->>Queue: OCR task (Google Doc AI)
  Note right of Queue: (optional: convert HEIC to JPG)
  Queue->>Google: OCR & structure (Doc AI)
  Google-->>Queue: JSON output
  Queue->>GPT: Send OCR to GPT with schema
  GPT-->>Queue: Extracted fields + confidence
  Queue->>DB: Update receipt fields + ai_review_json
```

#### Processing Steps:

1. **📤 S3 Upload** - Securely upload receipt images to AWS S3
2. **🔍 Google Document AI** - Extract text and structured data using Google's advanced OCR
3. **🤖 GPT Enhancement** - Enhance and validate data using OpenAI GPT-4 with confidence scoring
4. **✅ Data Validation** - Validate and score the extracted information

### 📊 Real-time Progress

- **Visual Flow Diagram** - See each step's progress with animated indicators
- **Live Updates** - Real-time status updates via polling
- **Progress Bars** - Individual step and overall completion tracking
- **Error Handling** - Clear error messages and retry capabilities

### 🎯 Key Features

- **Confidence Scoring** - AI provides confidence ratings for extracted data
- **Mock Mode** - Full development mode with simulated processing
- **Async Processing** - Non-blocking background processing
- **Session Management** - Track multiple processing sessions

### 📋 Receipt Record Lifecycle

Each receipt goes through the following states in the database:

#### 1. **Create Receipt Record** (Before Upload)
- Create new row in `receipts` table
- Set `user_id` to current user
- Set `status = "uploaded"`
- Set `source = "upload"` (or "email", etc.)
- Set `created_at = now()`

#### 2. **Upload Image to S3**
- Upload image file (JPG, PNG, or converted from HEIC)
- Update receipt record:
  - `s3_url = "<S3 file URL>"`
  - `filename = "<original filename>"`

#### 3. **Run OCR** (Google Document AI)
- Download or access the image
- Send to Google Document AI for OCR
- Parse and store:
  - `ocr_raw_text = "<full OCR output>"`
  - `status = "ocr_done"`

#### 4. **Extract Structured Fields** (via GPT)
- Use OCR text as input and ask GPT to extract:
  - `receipt_date`, `amount_total`, `vendor_name`, etc.
- Store the result:
  - `ai_review_json = "<full structured JSON output from GPT>"`
  - `ai_confidence_score = <float>` (e.g. 0.91)
  - `ai_reviewed_at = now()`
  - `status = "ai_done"`

#### 5. **Update Key Fields from AI Output**
- Extract values from `ai_review_json` into individual columns:
  - `receipt_date`, `amount_total`, `vendor_name`, `category`, etc.
- Optionally flag that these fields are not yet user-verified

#### 6. **Finalize / Ready for Review**
- If confidence score is high enough:
  - `status = "awaiting_user_review"`
- Else, flag for manual review:
  - `status = "ai_low_confidence"`
- If user confirms the data:
  - `is_verified = true`
  - `status = "verified"`

#### Status Values:
- `uploaded` - Initial state after file upload
- `ocr_done` - Google Document AI processing complete
- `ai_done` - GPT enhancement complete
- `ai_low_confidence` - Needs manual review due to low confidence
- `awaiting_user_review` - Ready for user verification
- `verified` - User has confirmed the data

### 🔧 Configuration

A comprehensive `.env` file has been created for development with all necessary settings:

```bash
# Copy the template and update with your values
cp env_template.txt .env
# Edit .env with your actual API keys
```

**Key Configuration Sections:**

#### 🔑 **AWS S3 Configuration**
```bash
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
S3_BUCKET_NAME=scouter-receipts-dev
AWS_DEFAULT_REGION=us-east-1
```

#### 🤖 **OpenAI Configuration**
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1500
```

#### 🔍 **Google Document AI Configuration**
```bash
# Required: Your Google Cloud Project ID
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id

# Required: Your Document AI Processor ID (long string from GCP Console)
GOOGLE_DOCUMENT_AI_PROCESSOR_ID=abc123def456ghi789...

# Optional: Location (default: us)
GOOGLE_CLOUD_LOCATION=us

# Authentication Options (choose one):

# Option 1: Local Development - Direct file path
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Option 2: AWS Production - Secrets Manager (Recommended)
AWS_SECRETS_MANAGER_SECRET_NAME=scouter/google-document-ai-key

# Option 3: Simple Base64 (Less secure)
# GOOGLE_SERVICE_ACCOUNT_JSON_B64=base64_encoded_json_here
```

**Authentication Options:**
1. **Service Account Key** (Recommended for development):
   - Download JSON key from Google Cloud Console
   - Set `GOOGLE_APPLICATION_CREDENTIALS` to file path
   
2. **Application Default Credentials** (Alternative for development):
   ```bash
   # Run once to authenticate
   gcloud auth application-default login
   # No GOOGLE_APPLICATION_CREDENTIALS needed
   ```
   
3. **Production Authentication**:
   - **AWS Deployment**: Service Account JSON key (stored securely)
   - **GCP Instances**: Use Instance Service Account
   - **GKE**: Use Workload Identity

#### ⚙️ **Processing Settings**
```bash
MAX_RECEIPT_SIZE=10485760  # 10MB
PROCESSING_TIMEOUT=60      # 60 seconds
DEBUG_PROCESSING_SESSIONS=True
```

**Note**: Without API keys, the system runs in mock mode with simulated processing. The `.env` file includes comprehensive development settings for all components.

## API Documentation

Scouter provides comprehensive API documentation using Redocly. The interactive documentation includes:

- 📚 **Complete API Reference** - All endpoints with detailed descriptions
- 🔍 **Interactive Examples** - Try API calls directly from the documentation
- 📝 **Request/Response Schemas** - Detailed data models and examples
- 🔐 **Authentication Guide** - How to use magic link authentication
- 📄 **Receipt Processing** - New endpoints for receipt processing pipeline

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

### Receipt Processing Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/receipt/process` | POST | Start receipt processing with real-time progress |
| `/api/receipt/progress/<session_id>` | GET | Get processing progress for a session |
| `/api/receipt/verify` | POST | Verify and save receipt data after human review |
| `/api/receipts` | GET | List all receipts for authenticated user |
| `/api/receipt/sessions` | GET | List active processing sessions (dev mode only) |

#### GET `/api/receipts`

Lists all receipts for the authenticated user.

**Authentication:** Required (session-based)

**Response:**
```json
{
  "receipts": [
    {
      "id": "uuid",
      "vendor_name": "Store Name",
      "receipt_date": "2025-09-30",
      "amount_total": 25.99,
      "amount_subtotal": 23.84,
      "tax_amount": 2.15,
      "currency": "USD",
      "category": "Groceries",
      "payment_method": "Credit Card",
      "location": "123 Main St",
      "upload_date": "2025-09-30T12:00:00",
      "status": "verified",
      "is_verified": true,
      "ai_result": { ... },
      "s3_url": "https://...",
      "document_ai_result": { ... }
    }
  ],
  "total": 42
}
```

**Features:**
- Returns receipts filtered by authenticated user
- Excludes deleted receipts (`is_deleted = False`)
- Orders by creation date (newest first)
- Includes full receipt data with AI analysis results

**Usage in Frontend:**
The frontend implements client-side filtering and pagination with:
- Free text search (vendor name and JSON data)
- Date range filtering
- Amount range filtering
- Tax amount range filtering
- Pagination (50/100/200 items per page)

#### POST `/api/receipt/verify`

Verifies and saves receipt data after human review.

**Authentication:** Required (session-based)

**Request Body:**
```json
{
  "receipt_id": "uuid",
  "verified_data": {
    "vendor_name": "Store Name",
    "receipt_date": "2025-09-30",
    "amount_total": 25.99,
    "tax_amount": 2.15,
    "currency": "USD",
    "category": "Groceries",
    "notes": "Optional notes"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Receipt verified successfully",
  "receipt_id": "uuid"
}
```

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

## Performance Monitoring with Prometheus & Grafana

Scouter includes built-in Prometheus metrics for monitoring receipt processing performance, costs, and quality.

### 📊 Available Metrics

#### **Overall Pipeline Metrics**
- `receipt_processing_duration_seconds` - Total end-to-end processing time (histogram)
- `receipt_processing_success_total` - Successfully processed receipts (counter)
- `receipt_processing_failed_total{step}` - Failed receipts by step (counter)
- `receipt_processing_in_progress` - Currently processing receipts (gauge)

#### **Per-Step Performance**
- `receipt_step_duration_seconds{step}` - Duration of each step: upload, ocr, ai, validation (histogram)

#### **Quality Metrics**
- `receipt_confidence_score` - AI confidence scores (histogram, 0-1.0)
- `receipt_human_review_required_total` - Receipts needing human review (counter)

#### **Cost Tracking**
- `receipt_ai_tokens_used_total{token_type}` - OpenAI tokens consumed (counter)
- `receipt_ai_cost_estimate_usd` - Estimated OpenAI API costs (counter)

#### **Additional Metrics**
- `receipt_upload_size_bytes` - Receipt image sizes (histogram)
- `receipt_verification_duration_seconds` - User verification time (histogram)

### 🚀 Quick Start with Prometheus

**1. Install Prometheus:**
```bash
# macOS
brew install prometheus

# Linux
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*
```

**2. Create Prometheus Configuration:**
```bash
cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'scouter'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
EOF
```

**3. Start Prometheus:**
```bash
prometheus --config.file=prometheus.yml
```

**4. Access Prometheus UI:**
```
http://localhost:9090
```

### 📈 Quick Start with Grafana

**1. Install Grafana:**
```bash
# macOS
brew install grafana
brew services start grafana

# Linux
sudo apt-get install -y grafana
sudo systemctl start grafana-server
```

**2. Access Grafana:**
```
http://localhost:3000
Default credentials: admin/admin
```

**3. Add Prometheus Data Source:**
- Click "Configuration" → "Data Sources" → "Add data source"
- Select "Prometheus"
- URL: `http://localhost:9090`
- Click "Save & Test"

**4. Create Dashboard:**

Use these sample queries:

**Processing Time (P95):**
```promql
histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m]))
```

**Success Rate:**
```promql
rate(receipt_processing_success_total[5m]) / (rate(receipt_processing_success_total[5m]) + rate(receipt_processing_failed_total[5m]))
```

**Throughput (receipts/minute):**
```promql
rate(receipt_processing_success_total[1m]) * 60
```

**Step Duration Breakdown:**
```promql
sum by (step) (rate(receipt_step_duration_seconds_sum[5m])) / sum by (step) (rate(receipt_step_duration_seconds_count[5m]))
```

**AI Cost per Hour:**
```promql
rate(receipt_ai_cost_estimate_usd[1h])
```

**Average Confidence Score:**
```promql
avg(receipt_confidence_score)
```

**Concurrent Processing:**
```promql
receipt_processing_in_progress
```

### 📊 Sample Grafana Dashboard JSON

Create a new dashboard and import this configuration:

```json
{
  "dashboard": {
    "title": "Scouter Receipt Processing",
    "panels": [
      {
        "title": "Processing Duration (P50, P95, P99)",
        "targets": [{
          "expr": "histogram_quantile(0.50, rate(receipt_processing_duration_seconds_bucket[5m]))",
          "legendFormat": "P50"
        }]
      },
      {
        "title": "Success vs Failed Receipts",
        "targets": [{
          "expr": "rate(receipt_processing_success_total[5m])",
          "legendFormat": "Success"
        }, {
          "expr": "rate(receipt_processing_failed_total[5m])",
          "legendFormat": "Failed"
        }]
      },
      {
        "title": "Step Duration Breakdown",
        "targets": [{
          "expr": "rate(receipt_step_duration_seconds_sum[5m]) / rate(receipt_step_duration_seconds_count[5m])",
          "legendFormat": "{{step}}"
        }]
      }
    ]
  }
}
```

### 🔍 Useful Prometheus Queries

**Find Slowest Step:**
```promql
topk(1, sum by (step) (rate(receipt_step_duration_seconds_sum[5m])) / sum by (step) (rate(receipt_step_duration_seconds_count[5m])))
```

**Failure Rate by Step:**
```promql
sum by (step) (rate(receipt_processing_failed_total[5m]))
```

**Daily Token Usage:**
```promql
increase(receipt_ai_tokens_used_total[24h])
```

**Low Confidence Rate:**
```promql
rate(receipt_human_review_required_total[1h]) / rate(receipt_processing_success_total[1h])
```

### 🎯 Recommended Alerts

Create these alerts in Prometheus `rules.yml`:

```yaml
groups:
  - name: scouter_alerts
    rules:
      - alert: HighFailureRate
        expr: rate(receipt_processing_failed_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High receipt processing failure rate"
          
      - alert: SlowProcessing
        expr: histogram_quantile(0.95, rate(receipt_processing_duration_seconds_bucket[5m])) > 60
        for: 10m
        annotations:
          summary: "Receipt processing is taking > 60 seconds (P95)"
          
      - alert: HighAICost
        expr: rate(receipt_ai_cost_estimate_usd[1h]) > 10
        for: 1h
        annotations:
          summary: "AI costs exceeding $10/hour"
```

### 📝 Testing Metrics

**1. View Raw Metrics:**
```bash
curl http://localhost:5001/metrics
```

**2. Process a Test Receipt:**
- Upload a receipt through the UI
- Check metrics update in real-time

**3. Query Metrics in Prometheus:**
- Go to `http://localhost:9090/graph`
- Enter metric name (e.g., `receipt_processing_duration_seconds`)
- Click "Execute" and "Graph"

### 🎨 Grafana Dashboard Tips

1. **Create Rows** for different metric categories:
   - Performance (duration, throughput)
   - Quality (confidence, human review rate)
   - Costs (tokens, API costs)
   - System Health (errors, concurrent processing)

2. **Use Variables** for dynamic filtering:
   - Step name (upload, ocr, ai, validation)
   - Time range
   - Percentile (P50, P95, P99)

3. **Set Up Alerts** in Grafana:
   - Notification channels (Slack, email, PagerDuty)
   - Alert rules based on thresholds
   - Alert history and acknowledgment

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

### Google Document AI Issues

**Authentication errors:**
```bash
# Check if credentials file exists and is readable
ls -la /path/to/service-account-key.json

# Test authentication
gcloud auth application-default print-access-token

# Alternative: Use gcloud auth for development
gcloud auth application-default login
```

**Common error messages:**
- `Failed to initialize Google Document AI` - Check credentials path
- `missing: GOOGLE_CLOUD_PROJECT_ID` - Set project ID in .env
- `missing: GOOGLE_DOCUMENT_AI_PROCESSOR_ID` - Set processor ID in .env
- `Permission denied` - Service account needs "Document AI API User" role

## Production Deployment

### AWS Deployment (Recommended)

#### 🔐 **Google Cloud Credentials on AWS**

Since you're using Google Document AI from AWS, you'll need to securely store the service account key:

**Option 1: AWS Secrets Manager (Recommended)**
```bash
# Store the JSON key in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "scouter/google-document-ai-key" \
  --description "Google Document AI Service Account Key" \
  --secret-string file://path/to/service-account-key.json

# In your application, retrieve the secret
# The app will write it to a temporary file and set GOOGLE_APPLICATION_CREDENTIALS
```

**Option 2: AWS Systems Manager Parameter Store**
```bash
# Store as SecureString parameter
aws ssm put-parameter \
  --name "/scouter/google-document-ai-key" \
  --type "SecureString" \
  --value file://path/to/service-account-key.json
```

**Option 3: Environment Variable (Less Secure)**
```bash
# Base64 encode the JSON key and set as environment variable
export GOOGLE_SERVICE_ACCOUNT_JSON_B64=$(base64 -i service-account-key.json)
```

#### 🚀 **AWS Deployment Options**

- **AWS ECS/Fargate**: Container-based deployment
- **AWS EC2**: Traditional server deployment  
- **AWS Lambda**: Serverless (with cold start considerations)
- **AWS Elastic Beanstalk**: Platform-as-a-Service

#### 🔒 **Security Best Practices for AWS**

1. **Never store JSON keys in code or environment files**
2. **Use AWS IAM roles for AWS services access**
3. **Store Google credentials in AWS Secrets Manager**
4. **Use HTTPS/TLS for all communications**
5. **Enable AWS CloudTrail for audit logging**
6. **Use AWS VPC for network isolation**

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