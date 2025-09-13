#!/usr/bin/env python3
"""
Test script to verify email functionality with MailHog
"""

import requests
import json

def test_magic_link_email():
    """Test sending a magic link email"""
    
    # Test with one of our seeded users
    test_email = "john.doe@acme.com"
    
    print(f"🧪 Testing magic link email for: {test_email}")
    print("=" * 50)
    
    try:
        # Send magic link request
        response = requests.post('http://localhost:5001/api/auth/send-magic-link', 
                               json={'email': test_email})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Magic link request successful!")
            print(f"📧 Message: {data['message']}")
            if data.get('mailhog_url'):
                print(f"🔗 MailHog UI: {data['mailhog_url']}")
            
            # Check MailHog for the email
            print("\n📬 Checking MailHog for emails...")
            mailhog_response = requests.get('http://localhost:8025/api/v1/messages')
            
            if mailhog_response.status_code == 200:
                messages = mailhog_response.json()
                if messages:
                    print(f"✅ Found {len(messages)} email(s) in MailHog!")
                    latest_message = messages[0]  # MailHog returns newest first
                    print(f"📧 To: {', '.join([addr['Mailbox'] + '@' + addr['Domain'] for addr in latest_message['To']])}")
                    print(f"📧 Subject: {latest_message['Content']['Headers']['Subject'][0]}")
                    print(f"📧 From: {latest_message['From']['Mailbox']}@{latest_message['From']['Domain']}")
                else:
                    print("❌ No emails found in MailHog")
            else:
                print(f"❌ Failed to check MailHog: {mailhog_response.status_code}")
                
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

if __name__ == "__main__":
    test_magic_link_email() 