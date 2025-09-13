#!/usr/bin/env python3
"""
Standalone Authentication Server for Scouter
Handles magic link authentication with local dev SMTP simulation.
"""

import json
import secrets
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail, Message
from models import db, Organization, User
from email_config import get_email_config, get_mailhog_info, validate_email_config, print_email_config
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for development

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scouter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration - automatically switches between MailHog and Amazon SES
email_config = get_email_config()
for key, value in email_config.items():
    app.config[key] = value

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# In-memory storage for development (use database in production)
magic_tokens: Dict[str, dict] = {}
authenticated_users: Dict[str, dict] = {}

# Configuration
TOKEN_EXPIRY_MINUTES = 15
DEV_MODE = True  # Set to False in production

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session ID in Authorization header
        session_id = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_data = authenticated_users.get(session_id)
        if not user_data:
            return jsonify({'error': 'Invalid session'}), 401
        
        if not user_data.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        
        # Update last activity
        user_data['last_activity'] = datetime.now()
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin_page(f):
    """Decorator to require admin authentication for HTML pages"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For HTML pages, check session from cookie or redirect to login
        session_id = request.cookies.get('session_id') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_id:
            return '''
            <!DOCTYPE html>
            <html><head><title>Access Denied</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>🔒 Access Denied</h1>
                <p>Admin access required. Please <a href="/">login</a> with an admin account.</p>
            </body></html>
            ''', 403
        
        user_data = authenticated_users.get(session_id)
        if not user_data or not user_data.get('is_admin', False):
            return '''
            <!DOCTYPE html>
            <html><head><title>Access Denied</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>🔒 Access Denied</h1>
                <p>Admin access required. Please <a href="/">login</a> with an admin account.</p>
            </body></html>
            ''', 403
        
        # Update last activity
        user_data['last_activity'] = datetime.now()
        
        return f(*args, **kwargs)
    return decorated_function

def generate_magic_token(email: str, is_new_user: bool = False) -> str:
    """Generate a secure magic token for email authentication"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    
    magic_tokens[token] = {
        'email': email,
        'expires_at': expires_at,
        'used': False,
        'is_new_user': is_new_user
    }
    
    return token

def cleanup_expired_tokens():
    """Remove expired tokens from memory"""
    now = datetime.now()
    expired_tokens = [
        token for token, data in magic_tokens.items()
        if data['expires_at'] < now
    ]
    
    for token in expired_tokens:
        del magic_tokens[token]

def send_magic_link_email(email: str, magic_link: str, user_name: str):
    """Send magic link email via MailHog"""
    try:
        msg = Message(
            subject="Your Scouter Magic Link 🔗",
            recipients=[email],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML email template
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Scouter Magic Link</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">👓 Scouter</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Your magic link is ready!</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 8px; margin-bottom: 30px;">
                <h2 style="color: #333; margin-top: 0;">Hi {user_name}! 👋</h2>
                <p>Click the button below to sign in to your Scouter account:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{magic_link}" style="background: #4f46e5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; font-size: 16px;">
                        🚀 Sign In to Scouter
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{magic_link}" style="color: #4f46e5; word-break: break-all;">{magic_link}</a>
                </p>
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    ⏰ <strong>This link will expire in {TOKEN_EXPIRY_MINUTES} minutes</strong> for your security.
                </p>
            </div>
            
            <div style="text-align: center; font-size: 12px; color: #666; border-top: 1px solid #eee; padding-top: 20px;">
                <p>If you didn't request this email, you can safely ignore it.</p>
                <p style="margin: 0;">Sent by Scouter • Receipt Processing Made Easy</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        msg.body = f"""
        Hi {user_name}!

        Click the link below to sign in to Scouter:
        {magic_link}

        This link will expire in {TOKEN_EXPIRY_MINUTES} minutes.

        If you didn't request this, you can safely ignore this email.

        --
        Scouter Team
        """
        
        mail.send(msg)
        
        print(f"📧 Magic link email sent to {email}")
        
        # Show MailHog info if in development
        mailhog_info = get_mailhog_info()
        if mailhog_info['enabled']:
            print(f"🔗 MailHog UI: {mailhog_info['web_ui']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

@app.route('/api/auth/send-magic-link', methods=['POST'])
def send_magic_link():
    """Send a magic link to the user's email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
            
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[-1]:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user exists in database
        user = User.query.filter_by(email=email).first()
        is_new_user = user is None
        
        if user and not user.is_active:
            return jsonify({'error': 'User account is inactive. Please contact your administrator.'}), 403
        
        # Clean up expired tokens
        cleanup_expired_tokens()
        
        # Generate magic token (include new_user flag in token data)
        token = generate_magic_token(email, is_new_user)
        
        # Create magic link
        base_url = request.host_url.rstrip('/')
        magic_link = f"{base_url}/index.html?token={token}"
        
        # Send email (use placeholder name for new users)
        user_name = user.name if user else email.split('@')[0].title()
        email_sent = send_magic_link_email(email, magic_link, user_name)
        if not email_sent:
            return jsonify({'error': 'Failed to send magic link email'}), 500
        
        # Get MailHog info for response
        mailhog_info = get_mailhog_info()
        
        return jsonify({
            'success': True,
            'message': f'Magic link sent to {email}',
            'is_new_user': is_new_user,
            'dev_mode': DEV_MODE,
            'mailhog_url': mailhog_info['web_ui'] if mailhog_info['enabled'] else None
        })
        
    except Exception as e:
        print(f"Error sending magic link: {e}")
        return jsonify({'error': 'Failed to send magic link'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify a magic token and authenticate the user or prompt for registration"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Clean up expired tokens
        cleanup_expired_tokens()
        
        # Check if token exists and is valid
        token_data = magic_tokens.get(token)
        if not token_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if token_data['used']:
            return jsonify({'error': 'Token has already been used'}), 401
        
        if token_data['expires_at'] < datetime.now():
            return jsonify({'error': 'Token has expired'}), 401
        
        email = token_data['email']
        is_new_user = token_data.get('is_new_user', False)
        
        if is_new_user:
            # For new users, return a special response to trigger registration modal
            return jsonify({
                'success': True,
                'requires_registration': True,
                'email': email,
                'token': token,  # Keep token for registration completion
                'message': 'Please complete your registration'
            })
        else:
            # Existing user flow
            user = User.query.filter_by(email=email).first()
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Mark token as used
            token_data['used'] = True
            
            # Update user's last login
            user.update_last_login()
            
            # Create authenticated session
            session_id = secrets.token_urlsafe(32)
            
            authenticated_users[session_id] = {
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'organization': user.organization.name,
                'is_admin': user.is_admin,
                'authenticated_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            print(f"✅ User authenticated: {user.name} ({user.email}) - {user.organization.name}")
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'organization': user.organization.name,
                    'is_admin': user.is_admin
                },
                'session_id': session_id,
                'message': 'Authentication successful'
            })
        
    except Exception as e:
        print(f"Error verifying token: {e}")
        return jsonify({'error': 'Failed to verify token'}), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        session_id = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not session_id:
            return jsonify({'authenticated': False}), 200
        
        user_data = authenticated_users.get(session_id)
        if not user_data:
            return jsonify({'authenticated': False}), 200
        
        # Update last activity
        user_data['last_activity'] = datetime.now()
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user_data['user_id'],
                'email': user_data['email'],
                'name': user_data['name'],
                'organization': user_data['organization']
            },
            'authenticated_at': user_data['authenticated_at'].isoformat()
        })
        
    except Exception as e:
        print(f"Error checking auth status: {e}")
        return jsonify({'error': 'Failed to check authentication status'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Complete user registration for new users"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        user_name = data.get('name', '').strip()
        org_name = data.get('organization', '').strip()
        
        if not all([token, user_name, org_name]):
            return jsonify({'error': 'Token, name, and organization are required'}), 400
        
        # Validate token
        token_data = magic_tokens.get(token)
        if not token_data or token_data['used'] or token_data['expires_at'] < datetime.now():
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if not token_data.get('is_new_user'):
            return jsonify({'error': 'Token is not for new user registration'}), 400
        
        email = token_data['email']
        
        # Check if user was created in the meantime
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create or find organization
        organization = Organization.query.filter_by(name=org_name).first()
        if not organization:
            organization = Organization(name=org_name)
            db.session.add(organization)
            db.session.flush()  # Get the ID without committing
        
        # Create user (set admin status for specific email)
        is_admin = email == 'natanaelsilva@gmail.com'
        user = User(
            email=email,
            name=user_name,
            org_id=organization.id,
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        
        # Mark token as used
        token_data['used'] = True
        
        # Update user's last login
        user.update_last_login()
        
        # Create authenticated session
        session_id = secrets.token_urlsafe(32)
        
        authenticated_users[session_id] = {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'organization': organization.name,
            'authenticated_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        print(f"🎉 New user registered: {user.name} ({user.email}) - {organization.name}")
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'organization': organization.name,
                'is_admin': user.is_admin
            },
            'session_id': session_id,
            'message': 'Registration and authentication successful'
        })
        
    except Exception as e:
        print(f"Error during registration: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to complete registration'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    try:
        session_id = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if session_id and session_id in authenticated_users:
            user_data = authenticated_users[session_id]
            del authenticated_users[session_id]
            print(f"👋 User logged out: {user_data['name']} ({user_data['email']}) - {user_data['organization']}")
        
        return jsonify({'success': True, 'message': 'Logged out successfully'})
        
    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({'error': 'Failed to logout'}), 500

@app.route('/index.html')
def serve_index():
    """Serve the Scouter HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/health')
@require_admin
def health_check_api():
    """Health check API endpoint - Admin only"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'dev_mode': DEV_MODE,
        'active_tokens': len(magic_tokens),
        'authenticated_users': len(authenticated_users)
    })

@app.route('/health')
@require_admin_page
def health_check_page():
    """Health check HTML page - Admin only"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'dev_mode': DEV_MODE,
        'active_tokens': len(magic_tokens),
        'authenticated_users': len(authenticated_users),
        'uptime': 'Server running',
        'version': '1.0.0'
    }
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
         <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>Scouter Health Check</title>
     <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>👓</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-800 mb-2">🏥 Scouter Health Check</h1>
                <p class="text-gray-600">System status and monitoring dashboard</p>
            </div>

            <!-- Status Cards -->
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <!-- System Status -->
                <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-medium text-gray-600">System Status</p>
                            <p class="text-2xl font-bold text-green-600">✅ Healthy</p>
                        </div>
                        <div class="bg-green-100 p-3 rounded-full">
                            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <!-- Development Mode -->
                <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 {"border-yellow-500" if health_data["dev_mode"] else "border-blue-500"}">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-medium text-gray-600">Environment</p>
                            <p class="text-2xl font-bold {"text-yellow-600" if health_data["dev_mode"] else "text-blue-600"}">
                                {"🔧 Development" if health_data["dev_mode"] else "🚀 Production"}
                            </p>
                        </div>
                        <div class="{"bg-yellow-100" if health_data["dev_mode"] else "bg-blue-100"} p-3 rounded-full">
                            <svg class="w-6 h-6 {"text-yellow-600" if health_data["dev_mode"] else "text-blue-600"}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                        </div>
                    </div>
                </div>

                <!-- Version -->
                <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-medium text-gray-600">Version</p>
                            <p class="text-2xl font-bold text-purple-600">{health_data["version"]}</p>
                        </div>
                        <div class="bg-purple-100 p-3 rounded-full">
                            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Detailed Metrics -->
            <div class="grid md:grid-cols-2 gap-6 mb-8">
                <!-- Authentication Metrics -->
                <div class="bg-white rounded-xl shadow-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">🔐 Authentication</h3>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600">Active Magic Tokens</span>
                            <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                                {health_data["active_tokens"]}
                            </span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600">Authenticated Users</span>
                            <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                                {health_data["authenticated_users"]}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- System Info -->
                <div class="bg-white rounded-xl shadow-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-800 mb-4">📊 System Info</h3>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600">Last Check</span>
                            <span class="text-sm text-gray-500" x-data="{{timestamp: '{health_data["timestamp"]}'}}" x-text="new Date(timestamp).toLocaleString()">
                                {health_data["timestamp"]}
                            </span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-gray-600">Uptime</span>
                            <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                                {health_data["uptime"]}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">🚀 Quick Actions</h3>
                <div class="flex flex-wrap gap-4">
                    <a href="/" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 inline-flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m7 7 5 5 5-5"></path>
                        </svg>
                        Go to Scouter App
                    </a>
                    <button onclick="refreshHealth()" class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 inline-flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        Refresh Status
                    </button>
                    <a href="/api/health" class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 inline-flex items-center">
                        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        API Endpoint
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div class="text-center mt-8 text-gray-500">
                <p>Scouter Authentication Server • Built with Flask & Tailwind CSS</p>
            </div>
        </div>
    </div>

    <script>
        function refreshHealth() {{
            window.location.reload();
        }}
    </script>
</body>
</html>'''

@app.route('/admin/users')
@require_admin_page
def admin_users_page():
    """Admin users management page"""
    users = User.query.join(Organization).all()
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin - Users Management</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>👓</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="mb-8">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">👥 Users Management</h1>
                    <p class="text-gray-600 mt-2">Manage all users and organizations in Scouter</p>
                </div>
                <div class="flex gap-4">
                    <a href="/health" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                        🏥 Health Check
                    </a>
                    <a href="/" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                        🏠 Back to App
                    </a>
                </div>
            </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-sm p-6 border">
                <div class="flex items-center">
                    <div class="bg-blue-100 p-3 rounded-full">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"></path>
                        </svg>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">Total Users</p>
                        <p class="text-2xl font-bold text-gray-900">{len(users)}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-sm p-6 border">
                <div class="flex items-center">
                    <div class="bg-green-100 p-3 rounded-full">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">Organizations</p>
                        <p class="text-2xl font-bold text-gray-900">{len(set(user.organization.name for user in users))}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-sm p-6 border">
                <div class="flex items-center">
                    <div class="bg-purple-100 p-3 rounded-full">
                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                        </svg>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">Admin Users</p>
                        <p class="text-2xl font-bold text-gray-900">{len([user for user in users if user.is_admin])}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Users Table -->
        <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-900">All Users</h2>
            </div>
            
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Org ID</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {"".join([f'''
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{user.id}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="text-sm font-medium text-gray-900">{user.name}</div>
                                    {"<span class='ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800'>Admin</span>" if user.is_admin else ""}
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{user.organization.name}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{user.org_id}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {"bg-green-100 text-green-800" if user.is_active else "bg-red-100 text-red-800"}">
                                    {"Active" if user.is_active else "Inactive"}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"}
                            </td>
                        </tr>
                        ''' for user in users])}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-sm text-gray-500">
            <p>Scouter Admin Panel • Built with Flask & Tailwind CSS</p>
        </div>
    </div>
</body>
</html>'''

@app.route('/')
def root():
    """Root endpoint - redirect to Scouter"""
    from flask import redirect, url_for
    return redirect(url_for('serve_index'))

if __name__ == '__main__':
    # Validate email configuration
    if not validate_email_config():
        print("❌ Invalid email configuration. Please check your settings.")
        exit(1)
    
    # Print current configuration
    print_email_config()
    
    print("\n🚀 Starting Scouter Authentication Server")
    print("="*50)
    print("📱 Scouter: http://localhost:5000/index.html")
    print("🏥 Health Check: http://localhost:5000/api/health")
    print("🔧 Development Mode: Enabled")
    
    mailhog_info = get_mailhog_info()
    if mailhog_info['enabled']:
        print("📧 Email Testing: MailHog enabled")
        print(f"📬 MailHog UI: {mailhog_info['web_ui']}")
    else:
        print("📧 Email: Amazon SES configured")
    
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 