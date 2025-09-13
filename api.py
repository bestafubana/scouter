#!/usr/bin/env python3
"""
Standalone Receipt Scanner API
This file is completely independent and can be moved to another project.
"""

import base64
import json
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ReceiptItem:
    name: str
    price: float
    quantity: int = 1

@dataclass
class ReceiptTotals:
    subtotal: float
    tax: float
    total: float
    tax_breakdown: Dict[str, float] = None

@dataclass
class MerchantInfo:
    name: str
    address: str = ""
    phone: str = ""

@dataclass
class TransactionInfo:
    date: str
    time: str = ""
    cashier: str = ""
    payment_method: str = ""
    approval_code: str = ""

@dataclass
class ReceiptData:
    merchant: MerchantInfo
    transaction: TransactionInfo
    items: List[ReceiptItem]
    totals: ReceiptTotals
    currency: str = "CAD"

class GoogleCloudVisionAPI:
    """
    Stub implementation for Google Cloud Vision API
    Replace with actual implementation when ready to deploy
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_GOOGLE_CLOUD_VISION_API_KEY"
        
    async def extract_text_from_image(self, image_data: str) -> str:
        """
        Extract text from image using Google Cloud Vision API
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Extracted text from the image
        """
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        print(f"🔍 [STUB] Calling Google Cloud Vision API...")
        print(f"📊 Image data size: {len(image_data)} characters")
        
        # Simulate API call delay
        await self._simulate_delay(1.5, 3.0)
        
        # In real implementation, you would:
        # 1. Prepare the request payload
        # 2. Make HTTP request to Google Cloud Vision API
        # 3. Parse the response and extract text
        # 4. Return the extracted text
        
        # Example real implementation structure:
        """
        import requests
        
        url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
        payload = {
            "requests": [{
                "image": {"content": image_data},
                "features": [{"type": "TEXT_DETECTION"}]
            }]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()
        
        if "textAnnotations" in result["responses"][0]:
            return result["responses"][0]["textAnnotations"][0]["description"]
        else:
            raise Exception("No text found in image")
        """
        
        # Mock response for development
        mock_receipt_text = """FRESH MARKET
123 Main Street
Vancouver, BC V6B 1A1
Tel: (604) 555-0123

Date: 2024-01-15
Time: 14:32:15
Cashier: John D.

ITEMS:
Organic Bananas       $3.99
Whole Milk 1L         $4.49
Bread - Whole Wheat   $2.99
Chicken Breast 1kg    $12.99
Broccoli              $2.49
Cheddar Cheese        $5.99

Subtotal:            $32.94
Tax (GST 5%):         $1.65
Tax (PST 7%):         $2.31
TOTAL:               $36.90

Payment: Visa ****1234
Approved: 123456

Thank you for shopping!"""
        
        print("✅ [STUB] Text extraction completed")
        return mock_receipt_text
    
    async def _simulate_delay(self, min_seconds: float, max_seconds: float):
        """Simulate API call delay for realistic testing"""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

class OpenAIAPI:
    """
    Stub implementation for OpenAI API
    Replace with actual implementation when ready to deploy
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_OPENAI_API_KEY"
        
    async def structure_receipt_data(self, raw_text: str) -> Dict[str, Any]:
        """
        Process raw receipt text and return structured JSON data
        
        Args:
            raw_text: Raw text extracted from receipt image
            
        Returns:
            Structured receipt data as dictionary
        """
        print(f"🤖 [STUB] Calling OpenAI API...")
        print(f"📝 Raw text length: {len(raw_text)} characters")
        
        # Simulate API call delay
        await self._simulate_delay(1.0, 2.5)
        
        # In real implementation, you would:
        # 1. Prepare the prompt for GPT
        # 2. Make HTTP request to OpenAI API
        # 3. Parse the response and validate JSON
        # 4. Return structured data
        
        # Example real implementation structure:
        """
        import openai
        
        client = openai.OpenAI(api_key=self.api_key)
        
        prompt = f'''
        Extract and structure the following receipt data into JSON format:
        
        {raw_text}
        
        Return a JSON object with the following structure:
        {{
            "merchant": {{"name": "", "address": "", "phone": ""}},
            "transaction": {{"date": "", "time": "", "cashier": "", "payment_method": "", "approval_code": ""}},
            "items": [{{"name": "", "price": 0.0, "quantity": 1}}],
            "totals": {{"subtotal": 0.0, "tax": 0.0, "total": 0.0, "tax_breakdown": {{}}}},
            "currency": "CAD"
        }}
        '''
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
        """
        
        # Mock structured response for development
        mock_structured_data = {
            "merchant": {
                "name": "Fresh Market",
                "address": "123 Main Street, Vancouver, BC V6B 1A1",
                "phone": "(604) 555-0123"
            },
            "transaction": {
                "date": "2024-01-15",
                "time": "14:32:15",
                "cashier": "John D.",
                "payment_method": "Visa ****1234",
                "approval_code": "123456"
            },
            "items": [
                {"name": "Organic Bananas", "price": 3.99, "quantity": 1},
                {"name": "Whole Milk 1L", "price": 4.49, "quantity": 1},
                {"name": "Bread - Whole Wheat", "price": 2.99, "quantity": 1},
                {"name": "Chicken Breast 1kg", "price": 12.99, "quantity": 1},
                {"name": "Broccoli", "price": 2.49, "quantity": 1},
                {"name": "Cheddar Cheese", "price": 5.99, "quantity": 1}
            ],
            "totals": {
                "subtotal": 32.94,
                "tax": 3.96,
                "total": 36.90,
                "tax_breakdown": {
                    "GST (5%)": 1.65,
                    "PST (7%)": 2.31
                }
            },
            "currency": "CAD"
        }
        
        print("✅ [STUB] Data structuring completed")
        return mock_structured_data
    
    async def _simulate_delay(self, min_seconds: float, max_seconds: float):
        """Simulate API call delay for realistic testing"""
        import random
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

class ReceiptProcessor:
    """
    Main receipt processing service
    Coordinates between Google Cloud Vision and OpenAI APIs
    """
    
    def __init__(self, vision_api_key: str = None, openai_api_key: str = None):
        self.vision_api = GoogleCloudVisionAPI(vision_api_key)
        self.openai_api = OpenAIAPI(openai_api_key)
    
    async def process_receipt(self, image_data: str) -> Dict[str, Any]:
        """
        Full receipt processing pipeline
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Structured receipt data
        """
        try:
            # Step 1: Extract text from image
            extracted_text = await self.vision_api.extract_text_from_image(image_data)
            
            # Step 2: Structure the data
            structured_data = await self.openai_api.structure_receipt_data(extracted_text)
            
            # Step 3: Add metadata
            structured_data["processing_metadata"] = {
                "processed_at": datetime.now().isoformat(),
                "raw_text_length": len(extracted_text),
                "processing_version": "1.0.0"
            }
            
            return structured_data
            
        except Exception as e:
            raise Exception(f"Receipt processing failed: {str(e)}")

# Example usage and testing functions
async def test_receipt_processor():
    """Test function to validate the receipt processor"""
    processor = ReceiptProcessor()
    
    # Mock image data (in real usage, this would come from the frontend)
    mock_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
    
    try:
        result = await processor.process_receipt(mock_image_data)
        print("✅ Receipt processing test successful!")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"❌ Receipt processing test failed: {e}")
        return None

if __name__ == "__main__":
    import asyncio
    
    print("🧪 Testing Receipt Scanner API...")
    asyncio.run(test_receipt_processor()) 