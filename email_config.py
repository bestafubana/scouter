"""
Email configuration for Scouter
Easily swap between MailHog (development) and Amazon SES (production)
"""

import os
from typing import Dict, Any

def get_email_config() -> Dict[str, Any]:
    """
    Get email configuration based on environment
    
    Returns:
        Dictionary with Flask-Mail configuration
    """
    
    # Check if we're in production mode
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if is_production:
        # Production configuration for Amazon SES
        return {
            'MAIL_SERVER': os.getenv('MAIL_SERVER', 'email-smtp.us-east-1.amazonaws.com'),
            'MAIL_PORT': int(os.getenv('MAIL_PORT', '587')),
            'MAIL_USE_TLS': True,
            'MAIL_USE_SSL': False,
            'MAIL_USERNAME': os.getenv('AWS_SES_USERNAME'),
            'MAIL_PASSWORD': os.getenv('AWS_SES_PASSWORD'),
            'MAIL_DEFAULT_SENDER': os.getenv('FROM_EMAIL', 'noreply@scouter.app'),
            'MAIL_DEBUG': False
        }
    else:
        # Development configuration for MailHog
        return {
            'MAIL_SERVER': 'localhost',
            'MAIL_PORT': 1025,
            'MAIL_USE_TLS': False,
            'MAIL_USE_SSL': False,
            'MAIL_USERNAME': None,
            'MAIL_PASSWORD': None,
            'MAIL_DEFAULT_SENDER': 'noreply@scouter.local',
            'MAIL_DEBUG': True
        }

def get_mailhog_info() -> Dict[str, Any]:
    """
    Get MailHog information for development
    
    Returns:
        Dictionary with MailHog URLs and info
    """
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    if is_production:
        return {
            'enabled': False,
            'web_ui': None,
            'smtp_server': None
        }
    else:
        return {
            'enabled': True,
            'web_ui': 'http://localhost:8025',
            'smtp_server': 'localhost:1025'
        }

def validate_email_config() -> bool:
    """
    Validate email configuration
    
    Returns:
        True if configuration is valid, False otherwise
    """
    config = get_email_config()
    
    # Check required fields
    required_fields = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_DEFAULT_SENDER']
    
    for field in required_fields:
        if not config.get(field):
            print(f"❌ Missing required email configuration: {field}")
            return False
    
    # For production, check SES credentials
    if os.getenv('FLASK_ENV') == 'production':
        if not config.get('MAIL_USERNAME') or not config.get('MAIL_PASSWORD'):
            print("❌ Missing AWS SES credentials for production")
            return False
    
    return True

def print_email_config():
    """Print current email configuration for debugging"""
    config = get_email_config()
    mailhog_info = get_mailhog_info()
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    print("\n📧 Email Configuration")
    print("=" * 40)
    print(f"Environment: {'Production' if is_production else 'Development'}")
    print(f"MAIL_SERVER: {config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {config['MAIL_PORT']}")
    print(f"MAIL_USE_TLS: {config['MAIL_USE_TLS']}")
    print(f"MAIL_DEFAULT_SENDER: {config['MAIL_DEFAULT_SENDER']}")
    
    if mailhog_info['enabled']:
        print(f"\n🔧 MailHog (Development)")
        print(f"Web UI: {mailhog_info['web_ui']}")
        print(f"SMTP: {mailhog_info['smtp_server']}")
    else:
        print(f"\n🚀 Amazon SES (Production)")
        print(f"Username: {config['MAIL_USERNAME']}")
    
    print("=" * 40)

# Example environment variables for different configurations

DEVELOPMENT_ENV_EXAMPLE = """
# Development (MailHog) - No environment variables needed
# Just start MailHog: mailhog &
"""

PRODUCTION_ENV_EXAMPLE = """
# Production (Amazon SES)
FLASK_ENV=production
AWS_SES_USERNAME=your_ses_smtp_username
AWS_SES_PASSWORD=your_ses_smtp_password
FROM_EMAIL=noreply@yourdomain.com
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com  # Optional, defaults to us-east-1
MAIL_PORT=587  # Optional, defaults to 587
""" 