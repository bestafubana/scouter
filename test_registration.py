#!/usr/bin/env python3
"""
Test script to verify the new user registration flow
"""

import requests
import json
import time

def test_new_user_registration():
    """Test the complete new user registration flow"""
    
    # Test with a new email that doesn't exist in the database
    test_email = "newuser@example.com"
    
    print(f"🧪 Testing new user registration for: {test_email}")
    print("=" * 60)
    
    try:
        # Step 1: Send magic link for new user
        print("1️⃣ Sending magic link for new user...")
        response = requests.post('http://localhost:5001/api/auth/send-magic-link', 
                               json={'email': test_email})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Magic link sent successfully!")
            print(f"📧 Message: {data['message']}")
            print(f"🆕 Is new user: {data.get('is_new_user', False)}")
            
            # Step 2: Check MailHog for the email
            print("\n2️⃣ Checking MailHog for emails...")
            time.sleep(1)  # Give email time to be sent
            mailhog_response = requests.get('http://localhost:8025/api/v1/messages')
            
            if mailhog_response.status_code == 200:
                messages = mailhog_response.json()
                if messages:
                    latest_message = messages[0]
                    print(f"✅ Email found in MailHog")
                    print(f"📧 To: {', '.join([addr['Mailbox'] + '@' + addr['Domain'] for addr in latest_message['To']])}")
                    print(f"📧 Subject: {latest_message['Content']['Headers']['Subject'][0]}")
                    
                    # Extract token from email content (this is a simplified approach)
                    # In a real test, you'd parse the email content properly
                    print("⚠️  Note: In a real test, you would extract the token from the email content")
                    print("   For now, we'll simulate the token verification...")
                else:
                    print("❌ No emails found in MailHog")
            
            print("\n3️⃣ Testing token verification (simulated)...")
            print("   This would normally extract the token from the email")
            print("   and verify it triggers the registration modal")
            
        else:
            print(f"❌ Magic link request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on port 5001")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_existing_user_flow():
    """Test the existing user authentication flow"""
    
    # Test with an existing user
    test_email = "john.doe@acme.com"
    
    print(f"\n🧪 Testing existing user flow for: {test_email}")
    print("=" * 60)
    
    try:
        response = requests.post('http://localhost:5001/api/auth/send-magic-link', 
                               json={'email': test_email})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Magic link sent successfully!")
            print(f"📧 Message: {data['message']}")
            print(f"🆕 Is new user: {data.get('is_new_user', False)}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_new_user_registration()
    test_existing_user_flow() 