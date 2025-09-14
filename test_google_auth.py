#!/usr/bin/env python3
"""
Test script to verify Google Document AI authentication setup
Run this to check if your Google Cloud credentials are configured correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_document_ai_auth():
    """Test Google Document AI authentication and configuration"""
    
    print("🧪 Testing Google Document AI Authentication")
    print("=" * 50)
    
    # Check required environment variables
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    processor_id = os.getenv('GOOGLE_DOCUMENT_AI_PROCESSOR_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"📋 Configuration Check:")
    print(f"   Project ID: {'✅ Set' if project_id else '❌ Missing'}")
    print(f"   Processor ID: {'✅ Set' if processor_id else '❌ Missing'}")
    print(f"   Credentials Path: {'✅ Set' if credentials_path else '⚠️  Using Application Default Credentials'}")
    
    if credentials_path:
        if os.path.exists(credentials_path):
            print(f"   Credentials File: ✅ Found at {credentials_path}")
        else:
            print(f"   Credentials File: ❌ Not found at {credentials_path}")
            return False
    
    if not project_id or not processor_id:
        print(f"\n❌ Missing required configuration. Please set:")
        if not project_id:
            print(f"   GOOGLE_CLOUD_PROJECT_ID=your-project-id")
        if not processor_id:
            print(f"   GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your-processor-id")
        return False
    
    # Try to import and initialize the client
    try:
        from google.cloud import documentai
        print(f"\n📦 Google Cloud Document AI library: ✅ Installed")
    except ImportError:
        print(f"\n📦 Google Cloud Document AI library: ❌ Not installed")
        print(f"   Run: pip install google-cloud-documentai")
        return False
    
    # Try to create client
    try:
        client = documentai.DocumentProcessorServiceClient()
        processor_name = client.processor_path(project_id, "us", processor_id)
        print(f"\n🔑 Authentication: ✅ Successfully created client")
        print(f"   Processor Path: {processor_name}")
        
        # Try to get processor info (this will test actual API access)
        try:
            processor = client.get_processor(name=processor_name)
            print(f"   Processor Name: {processor.display_name}")
            print(f"   Processor Type: {processor.type_}")
            print(f"   Processor State: {processor.state.name}")
            print(f"\n🎉 Google Document AI is fully configured and accessible!")
            return True
            
        except Exception as api_error:
            print(f"\n⚠️  Client created but API call failed:")
            print(f"   Error: {api_error}")
            print(f"   This might be a permissions issue or invalid processor ID")
            
            # Check common issues
            if "403" in str(api_error):
                print(f"\n💡 Troubleshooting:")
                print(f"   - Ensure your service account has 'Document AI API User' role")
                print(f"   - Verify the Document AI API is enabled in your project")
            elif "404" in str(api_error):
                print(f"\n💡 Troubleshooting:")
                print(f"   - Check that the processor ID is correct")
                print(f"   - Ensure the processor exists in the specified project")
            
            return False
            
    except Exception as client_error:
        print(f"\n❌ Failed to create Document AI client:")
        print(f"   Error: {client_error}")
        
        print(f"\n💡 Troubleshooting:")
        if "could not find default credentials" in str(client_error).lower():
            print(f"   - Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file")
            print(f"   - Or run: gcloud auth application-default login")
        else:
            print(f"   - Check your Google Cloud credentials")
            print(f"   - Verify the service account has proper permissions")
        
        return False

def test_alternative_auth():
    """Test if gcloud Application Default Credentials are available"""
    print(f"\n🔧 Testing Alternative Authentication Methods:")
    
    try:
        import subprocess
        result = subprocess.run(
            ['gcloud', 'auth', 'application-default', 'print-access-token'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"   Application Default Credentials: ✅ Available")
            print(f"   You can use Document AI without GOOGLE_APPLICATION_CREDENTIALS")
            return True
        else:
            print(f"   Application Default Credentials: ❌ Not configured")
            print(f"   Run: gcloud auth application-default login")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"   gcloud CLI: ❌ Not installed or not in PATH")
        return False

if __name__ == "__main__":
    print(f"Google Document AI Authentication Test")
    print(f"This script helps verify your Google Cloud setup\n")
    
    success = test_google_document_ai_auth()
    
    if not success:
        test_alternative_auth()
        print(f"\n📖 For detailed setup instructions, see:")
        print(f"   https://cloud.google.com/document-ai/docs/setup")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed! Google Document AI is ready to use.")
        sys.exit(0)
