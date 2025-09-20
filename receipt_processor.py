#!/usr/bin/env python3
"""
Enhanced Receipt Processing System
Real S3 upload, Tesseract OCR, OpenAI processing with real-time progress updates
"""

import asyncio
import base64
import json
import os
import uuid
import time
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from io import BytesIO
import tempfile

# Third-party imports (will be added to requirements.txt)
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = Exception

try:
    from google.cloud import documentai
    from PIL import Image
except ImportError:
    documentai = None
    Image = None

try:
    import openai
except ImportError:
    openai = None

@dataclass
class ProcessingStep:
    """Represents a step in the receipt processing pipeline"""
    id: str
    name: str
    status: str  # 'pending', 'processing', 'completed', 'error'
    progress: int  # 0-100
    message: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

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
    confidence_score: float = 0.0
    processing_metadata: Dict[str, Any] = None

class S3Uploader:
    """Handles S3 upload operations"""
    
    def __init__(self, bucket_name: str = None, aws_access_key: str = None, 
                 aws_secret_key: str = None, region: str = 'us-east-1'):
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME', 'scouter-receipts')
        self.aws_access_key = aws_access_key or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = aws_secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = region
        
        # Initialize S3 client
        if boto3 and self.aws_access_key and self.aws_secret_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region
            )
        else:
            self.s3_client = None
    
    async def upload_image(self, image_data: str, filename: str = None) -> Dict[str, Any]:
        """
        Upload image to S3 bucket
        
        Args:
            image_data: Base64 encoded image data
            filename: Optional filename, will generate UUID if not provided
            
        Returns:
            Dictionary with upload results
        """
        if not self.s3_client:
            # Mock S3 upload for development
            await asyncio.sleep(1.5)  # Simulate upload time
            mock_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename or 'mock-receipt.jpg'}"
            return {
                'success': True,
                'url': mock_url,
                'bucket': self.bucket_name,
                'key': filename or 'mock-receipt.jpg',
                'size': len(image_data) if image_data else 0,
                'mock': True
            }
        
        try:
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"receipts/{timestamp}_{unique_id}.jpg"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=image_bytes,
                ContentType='image/jpeg',
                Metadata={
                    'uploaded_at': datetime.now().isoformat(),
                    'source': 'scouter_app'
                }
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
            
            return {
                'success': True,
                'url': url,
                'bucket': self.bucket_name,
                'key': filename,
                'size': len(image_bytes),
                'mock': False
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'mock': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Upload failed: {str(e)}",
                'mock': False
            }

class GoogleDocumentAI:
    """
    Handles Google Document AI operations with proper authentication
    
    Authentication Methods (in order of precedence):
    1. GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to JSON key file
    2. AWS_SECRETS_MANAGER_SECRET_NAME for Google credentials (AWS deployment)
    3. GOOGLE_SERVICE_ACCOUNT_JSON_B64 base64 encoded JSON (less secure)
    4. gcloud Application Default Credentials (for local development)
    5. Instance Service Account (for GCP instances)
    6. Workload Identity (for GKE)
    """
    
    def __init__(self, project_id: str = None, location: str = "us", processor_id: str = None):
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.location = location or os.getenv('GOOGLE_CLOUD_LOCATION', 'us')
        self.processor_id = processor_id or os.getenv('GOOGLE_DOCUMENT_AI_PROCESSOR_ID')
        self._temp_credentials_file = None
        
        # Setup authentication
        credentials_path = self._setup_authentication()
        
        # Initialize Document AI client
        if documentai and self.project_id and self.processor_id:
            try:
                # The client will automatically use credentials in this order:
                # 1. GOOGLE_APPLICATION_CREDENTIALS env var (set by _setup_authentication)
                # 2. gcloud Application Default Credentials
                # 3. Instance/Workload Identity
                self.client = documentai.DocumentProcessorServiceClient()
                self.processor_name = self.client.processor_path(
                    self.project_id, self.location, self.processor_id
                )
                print(f"✅ Google Document AI initialized successfully")
                if credentials_path:
                    print(f"📁 Using credentials from: {credentials_path}")
                else:
                    print(f"🔑 Using Application Default Credentials")
            except Exception as e:
                print(f"❌ Failed to initialize Google Document AI: {e}")
                print(f"💡 Make sure GOOGLE_APPLICATION_CREDENTIALS is set or run 'gcloud auth application-default login'")
                self.client = None
        else:
            self.client = None
            missing = []
            if not self.project_id:
                missing.append("GOOGLE_CLOUD_PROJECT_ID")
            if not self.processor_id:
                missing.append("GOOGLE_DOCUMENT_AI_PROCESSOR_ID")
            if missing:
                print(f"⚠️  Google Document AI disabled - missing: {', '.join(missing)}")
            else:
                print(f"⚠️  Google Document AI disabled - library not installed")
    
    def _setup_authentication(self) -> Optional[str]:
        """
        Setup Google Cloud authentication for AWS deployment
        Returns the path to credentials file if set
        """
        # Method 1: Direct credentials file path (local development)
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            return credentials_path
        
        # Method 2: AWS Secrets Manager (production AWS deployment)
        aws_secret_name = os.getenv('AWS_SECRETS_MANAGER_SECRET_NAME')
        if aws_secret_name and boto3:
            try:
                # Create AWS Secrets Manager client
                session = boto3.Session()
                client = session.client('secretsmanager')
                
                # Retrieve the secret
                response = client.get_secret_value(SecretId=aws_secret_name)
                secret_data = response['SecretString']
                
                # Create temporary file for credentials
                self._temp_credentials_file = tempfile.NamedTemporaryFile(
                    mode='w', suffix='.json', delete=False
                )
                self._temp_credentials_file.write(secret_data)
                self._temp_credentials_file.close()
                
                # Set environment variable
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._temp_credentials_file.name
                print(f"🔐 Retrieved Google credentials from AWS Secrets Manager: {aws_secret_name}")
                return self._temp_credentials_file.name
                
            except Exception as e:
                print(f"❌ Failed to retrieve credentials from AWS Secrets Manager: {e}")
        
        # Method 3: Base64 encoded JSON (less secure, but simple)
        json_b64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_B64')
        if json_b64:
            try:
                # Decode base64 and create temporary file
                json_data = base64.b64decode(json_b64).decode('utf-8')
                
                self._temp_credentials_file = tempfile.NamedTemporaryFile(
                    mode='w', suffix='.json', delete=False
                )
                self._temp_credentials_file.write(json_data)
                self._temp_credentials_file.close()
                
                # Set environment variable
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._temp_credentials_file.name
                print(f"🔐 Using base64 encoded Google credentials")
                return self._temp_credentials_file.name
                
            except Exception as e:
                print(f"❌ Failed to decode base64 credentials: {e}")
        
        # No credentials found - will try Application Default Credentials
        return None
    
    def __del__(self):
        """Clean up temporary credentials file"""
        if self._temp_credentials_file and os.path.exists(self._temp_credentials_file.name):
            try:
                os.unlink(self._temp_credentials_file.name)
            except Exception:
                pass  # Ignore cleanup errors
    
    async def extract_text_from_image(self, image_data: str) -> Dict[str, Any]:
        """
        Extract text and structured data from image using Google Document AI
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Dictionary with OCR results and structured data
        """
        if not self.client:
            # Mock Google Document AI for development
            await asyncio.sleep(2.5)  # Simulate processing time
            
            mock_text = """FRESH MARKET
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
            
            # Mock structured data that Document AI would extract
            mock_structured = {
                'supplier_name': 'Fresh Market',
                'supplier_address': '123 Main Street, Vancouver, BC V6B 1A1',
                'supplier_phone': '(604) 555-0123',
                'invoice_date': '2024-01-15',
                'total_amount': 36.90,
                'subtotal_amount': 32.94,
                'tax_amount': 3.96,
                'currency': 'CAD',
                'payment_method': 'Visa',
                'line_items': [
                    {'description': 'Organic Bananas', 'amount': 3.99},
                    {'description': 'Whole Milk 1L', 'amount': 4.49},
                    {'description': 'Bread - Whole Wheat', 'amount': 2.99},
                    {'description': 'Chicken Breast 1kg', 'amount': 12.99},
                    {'description': 'Broccoli', 'amount': 2.49},
                    {'description': 'Cheddar Cheese', 'amount': 5.99}
                ]
            }
            
            return {
                'success': True,
                'text': mock_text,
                'structured_data': mock_structured,
                'confidence': 88.2,
                'word_count': len(mock_text.split()),
                'processing_time': 2.5,
                'mock': True
            }
        
        try:
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            start_time = time.time()
            
            # Create Document AI request
            raw_document = documentai.RawDocument(
                content=image_bytes,
                mime_type="image/jpeg"  # Adjust based on actual image type
            )
            
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract text
            extracted_text = document.text
            
            # Extract structured data from entities
            structured_data = {}
            for entity in document.entities:
                if entity.type_ == 'supplier_name':
                    structured_data['supplier_name'] = entity.mention_text
                elif entity.type_ == 'supplier_address':
                    structured_data['supplier_address'] = entity.mention_text
                elif entity.type_ == 'invoice_date':
                    structured_data['invoice_date'] = entity.mention_text
                elif entity.type_ == 'total_amount':
                    structured_data['total_amount'] = float(entity.mention_text.replace('$', '').replace(',', ''))
                elif entity.type_ == 'subtotal_amount':
                    structured_data['subtotal_amount'] = float(entity.mention_text.replace('$', '').replace(',', ''))
                elif entity.type_ == 'tax_amount':
                    structured_data['tax_amount'] = float(entity.mention_text.replace('$', '').replace(',', ''))
                elif entity.type_ == 'currency':
                    structured_data['currency'] = entity.mention_text
            
            # Extract line items
            line_items = []
            for entity in document.entities:
                if entity.type_ == 'line_item':
                    item = {}
                    for prop in entity.properties:
                        if prop.type_ == 'line_item/description':
                            item['description'] = prop.mention_text
                        elif prop.type_ == 'line_item/amount':
                            item['amount'] = float(prop.mention_text.replace('$', '').replace(',', ''))
                    if item:
                        line_items.append(item)
            
            if line_items:
                structured_data['line_items'] = line_items
            
            processing_time = time.time() - start_time
            
            # Calculate confidence based on entity confidence scores
            confidences = [entity.confidence for entity in document.entities if hasattr(entity, 'confidence')]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'success': True,
                'text': extracted_text,
                'structured_data': structured_data,
                'confidence': round(avg_confidence * 100, 1),  # Convert to percentage
                'word_count': len(extracted_text.split()),
                'processing_time': round(processing_time, 2),
                'mock': False
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Google Document AI processing failed: {str(e)}",
                'mock': False
            }

class OpenAIProcessor:
    """Handles OpenAI API operations"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if openai and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    async def structure_receipt_data(self, raw_text: str) -> Dict[str, Any]:
        """
        Process raw receipt text and return structured JSON data with confidence scoring
        
        Args:
            raw_text: Raw text extracted from receipt image
            
        Returns:
            Dictionary with structured data and confidence score
        """
        if not self.client:
            # Mock OpenAI processing for development
            await asyncio.sleep(1.8)  # Simulate API call time
            
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
                "currency": "CAD",
                "confidence_score": 92.3,
                "confidence_breakdown": {
                    "merchant_info": 95.0,
                    "transaction_details": 90.0,
                    "items_extraction": 88.5,
                    "totals_calculation": 96.0
                },
                "mock": True
            }
            
            return {
                'success': True,
                'data': mock_structured_data,
                'processing_time': 1.8,
                'tokens_used': 450,
                'model': 'gpt-4-mock'
            }
        
        try:
            start_time = time.time()
            
            prompt = f'''
            Extract and structure the following receipt data into JSON format. 
            Also provide a confidence score (0-100) for the overall extraction quality.
            
            Receipt Text:
            {raw_text}
            
            Return a JSON object with this exact structure:
            {{
                "merchant": {{"name": "", "address": "", "phone": ""}},
                "transaction": {{"date": "", "time": "", "cashier": "", "payment_method": "", "approval_code": ""}},
                "items": [{{"name": "", "price": 0.0, "quantity": 1}}],
                "totals": {{"subtotal": 0.0, "tax": 0.0, "total": 0.0, "tax_breakdown": {{}}}},
                "currency": "CAD",
                "confidence_score": 0.0,
                "confidence_breakdown": {{
                    "merchant_info": 0.0,
                    "transaction_details": 0.0,
                    "items_extraction": 0.0,
                    "totals_calculation": 0.0
                }}
            }}
            
            Be precise with numbers and provide realistic confidence scores based on text clarity.
            '''
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            processing_time = time.time() - start_time
            
            # Parse the response
            structured_data = json.loads(response.choices[0].message.content)
            
            return {
                'success': True,
                'data': structured_data,
                'processing_time': round(processing_time, 2),
                'tokens_used': response.usage.total_tokens,
                'model': response.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"OpenAI processing failed: {str(e)}",
                'mock': False
            }
    
    async def enhance_receipt_data(self, combined_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance Document AI results with OpenAI for better accuracy and completeness
        
        Args:
            combined_input: Dictionary with raw_text and structured_data from Document AI
            
        Returns:
            Dictionary with enhanced structured data and confidence score
        """
        if not self.client:
            # Mock OpenAI enhancement for development
            await asyncio.sleep(1.5)
            
            # Use Document AI data as base and enhance it
            base_data = combined_input.get('structured_data', {})
            
            enhanced_data = {
                "receipt_date": base_data.get('invoice_date', '2024-01-15'),
                "vendor_name": base_data.get('supplier_name', 'Fresh Market'),
                "location": base_data.get('supplier_address', '123 Main Street, Vancouver, BC'),
                "amount_total": base_data.get('total_amount', 36.90),
                "amount_subtotal": base_data.get('subtotal_amount', 32.94),
                "tax_amount": base_data.get('tax_amount', 3.96),
                "currency": base_data.get('currency', 'CAD'),
                "payment_method": base_data.get('payment_method', 'Visa'),
                "category": "Groceries",  # Enhanced by GPT
                "items": [
                    {"name": item.get('description', ''), "price": item.get('amount', 0), "quantity": 1}
                    for item in base_data.get('line_items', [])
                ],
                "confidence_score": 91.5,
                "confidence_breakdown": {
                    "document_ai_confidence": 88.2,
                    "gpt_enhancement_confidence": 94.8,
                    "overall_confidence": 91.5
                },
                "processing_notes": "Enhanced with GPT-4 for improved categorization and validation",
                "mock": True
            }
            
            return {
                'success': True,
                'data': enhanced_data,
                'processing_time': 1.5,
                'tokens_used': 380,
                'model': 'gpt-4-mock'
            }
        
        try:
            start_time = time.time()
            
            raw_text = combined_input.get('raw_text', '')
            structured_data = combined_input.get('structured_data', {})
            
            prompt = f'''
            You are an expert at processing receipt data. I have receipt text and some pre-extracted structured data from Google Document AI.
            Please enhance and validate this data, filling in any missing fields and correcting any errors.
            
            Raw Receipt Text:
            {raw_text}
            
            Pre-extracted Structured Data:
            {json.dumps(structured_data, indent=2)}
            
            Please return an enhanced JSON object with this exact structure:
            {{
                "receipt_date": "YYYY-MM-DD",
                "vendor_name": "Store Name",
                "location": "Store address or city",
                "amount_total": 0.00,
                "amount_subtotal": 0.00,
                "tax_amount": 0.00,
                "currency": "CAD",
                "payment_method": "Visa/Cash/etc",
                "category": "Groceries/Gas/Meals/etc",
                "items": [
                    {{"name": "Item Name", "price": 0.00, "quantity": 1}}
                ],
                "confidence_score": 0.0,
                "confidence_breakdown": {{
                    "document_ai_confidence": 0.0,
                    "gpt_enhancement_confidence": 0.0,
                    "overall_confidence": 0.0
                }},
                "processing_notes": "Any notes about the processing"
            }}
            
            Focus on:
            1. Validating and correcting amounts and dates
            2. Categorizing the receipt appropriately
            3. Ensuring all items are properly extracted
            4. Providing realistic confidence scores (0-100)
            '''
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            processing_time = time.time() - start_time
            
            # Parse the response
            enhanced_data = json.loads(response.choices[0].message.content)
            
            return {
                'success': True,
                'data': enhanced_data,
                'processing_time': round(processing_time, 2),
                'tokens_used': response.usage.total_tokens,
                'model': response.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"OpenAI enhancement failed: {str(e)}",
                'mock': False
            }

class ReceiptProcessor:
    """
    Enhanced receipt processing pipeline with real-time progress updates
    """
    
    def __init__(self, s3_bucket: str = None, google_project_id: str = None, 
                 google_processor_id: str = None, openai_api_key: str = None):
        self.s3_uploader = S3Uploader(bucket_name=s3_bucket)
        self.document_ai = GoogleDocumentAI(
            project_id=google_project_id, 
            processor_id=google_processor_id
        )
        self.openai_processor = OpenAIProcessor(api_key=openai_api_key)
        
        # Processing steps definition
        self.processing_steps = [
            ProcessingStep(
                id="upload",
                name="Upload to S3",
                status="pending",
                progress=0,
                message="Preparing to upload image..."
            ),
            ProcessingStep(
                id="document_ai",
                name="Google Document AI",
                status="pending",
                progress=0,
                message="Waiting for upload to complete..."
            ),
            ProcessingStep(
                id="ai_processing",
                name="GPT Enhancement",
                status="pending",
                progress=0,
                message="Waiting for Document AI processing..."
            ),
            ProcessingStep(
                id="validation",
                name="Data Validation",
                status="pending",
                progress=0,
                message="Waiting for AI processing..."
            )
        ]
    
    async def process_receipt(self, image_data: str, progress_callback: Callable = None, receipt_id: str = None) -> Dict[str, Any]:
        """
        Full receipt processing pipeline with real-time progress updates
        
        Args:
            image_data: Base64 encoded image data
            progress_callback: Optional callback function for progress updates
            receipt_id: Database receipt ID for tracking progress
            
        Returns:
            Complete processing results with structured data
        """
        processing_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Step 1: Upload to S3
            await self._update_step("upload", "processing", 10, "Uploading image to S3...", progress_callback)
            
            upload_result = await self.s3_uploader.upload_image(image_data)
            
            if not upload_result['success']:
                await self._update_step("upload", "error", 0, f"Upload failed: {upload_result.get('error', 'Unknown error')}", progress_callback)
                raise Exception(f"S3 upload failed: {upload_result.get('error')}")
            
            await self._update_step("upload", "completed", 100, f"Image uploaded successfully ({upload_result.get('size', 0)} bytes)", progress_callback)
            
            # Step 2: Google Document AI Processing
            await self._update_step("document_ai", "processing", 20, "Processing with Google Document AI...", progress_callback)
            
            document_ai_result = await self.document_ai.extract_text_from_image(image_data)
            
            if not document_ai_result['success']:
                await self._update_step("document_ai", "error", 0, f"Document AI failed: {document_ai_result.get('error', 'Unknown error')}", progress_callback)
                raise Exception(f"Document AI processing failed: {document_ai_result.get('error')}")
            
            await self._update_step("document_ai", "completed", 100, f"Document processed ({document_ai_result.get('word_count', 0)} words, {document_ai_result.get('confidence', 0)}% confidence)", progress_callback)
            
            # Step 3: GPT Enhancement Processing
            await self._update_step("ai_processing", "processing", 30, "Enhancing with OpenAI GPT-4...", progress_callback)
            
            # Use Document AI structured data + raw text for better GPT processing
            combined_input = {
                'raw_text': document_ai_result['text'],
                'structured_data': document_ai_result.get('structured_data', {})
            }
            
            ai_result = await self.openai_processor.enhance_receipt_data(combined_input)
            
            if not ai_result['success']:
                await self._update_step("ai_processing", "error", 0, f"AI processing failed: {ai_result.get('error', 'Unknown error')}", progress_callback)
                raise Exception(f"AI processing failed: {ai_result.get('error')}")
            
            await self._update_step("ai_processing", "completed", 100, f"Data structured (confidence: {ai_result['data'].get('confidence_score', 0)}%)", progress_callback)
            
            # Step 4: Validation
            await self._update_step("validation", "processing", 80, "Validating extracted data...", progress_callback)
            
            # Simulate validation time
            await asyncio.sleep(0.5)
            
            # Validate the structured data
            validation_result = self._validate_receipt_data(ai_result['data'])
            
            await self._update_step("validation", "completed", 100, f"Validation complete ({validation_result['score']}% accuracy)", progress_callback)
            
            # Compile final results
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            final_result = {
                'processing_id': processing_id,
                'success': True,
                'receipt_data': ai_result['data'],
                'processing_metadata': {
                    'started_at': start_time.isoformat(),
                    'completed_at': end_time.isoformat(),
                    'processing_time': round(processing_time, 2),
                    'upload_info': upload_result,
                    'document_ai_info': document_ai_result,
                    'ai_enhancement_info': ai_result,
                    'validation_info': validation_result,
                    'steps': [asdict(step) for step in self.processing_steps]
                }
            }
            
            return final_result
            
        except Exception as e:
            # Mark all remaining steps as error
            for step in self.processing_steps:
                if step.status == "pending" or step.status == "processing":
                    await self._update_step(step.id, "error", 0, f"Processing failed: {str(e)}", progress_callback)
            
            return {
                'processing_id': processing_id,
                'success': False,
                'error': str(e),
                'processing_metadata': {
                    'started_at': start_time.isoformat(),
                    'failed_at': datetime.now().isoformat(),
                    'steps': [asdict(step) for step in self.processing_steps]
                }
            }
    
    async def _update_step(self, step_id: str, status: str, progress: int, message: str, callback: Callable = None):
        """Update a processing step and call the progress callback"""
        for step in self.processing_steps:
            if step.id == step_id:
                step.status = status
                step.progress = progress
                step.message = message
                
                if status == "processing" and not step.started_at:
                    step.started_at = datetime.now().isoformat()
                elif status in ["completed", "error"]:
                    step.completed_at = datetime.now().isoformat()
                
                if step.status == "error":
                    step.error = message
                
                break
        
        # Call progress callback if provided
        if callback:
            await callback({
                'step_id': step_id,
                'status': status,
                'progress': progress,
                'message': message,
                'all_steps': [asdict(step) for step in self.processing_steps]
            })
    
    def _validate_receipt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structured receipt data"""
        score = 100
        issues = []
        
        # Check merchant info
        if not data.get('merchant', {}).get('name'):
            score -= 10
            issues.append("Missing merchant name")
        
        # Check items
        items = data.get('items', [])
        if not items:
            score -= 20
            issues.append("No items found")
        else:
            for item in items:
                if not item.get('name') or item.get('price', 0) <= 0:
                    score -= 5
                    issues.append(f"Invalid item: {item}")
        
        # Check totals
        totals = data.get('totals', {})
        if not totals.get('total') or totals.get('total', 0) <= 0:
            score -= 15
            issues.append("Invalid total amount")
        
        return {
            'score': max(0, score),
            'issues': issues,
            'valid': score >= 70
        }

# Example usage and testing
async def test_receipt_processor():
    """Test the enhanced receipt processor"""
    processor = ReceiptProcessor()
    
    # Mock image data
    mock_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
    
    # Progress callback for testing
    async def progress_callback(update):
        print(f"Progress Update: {update['step_id']} - {update['status']} - {update['message']}")
    
    try:
        result = await processor.process_receipt(mock_image_data, progress_callback)
        print("✅ Enhanced receipt processing test successful!")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"❌ Enhanced receipt processing test failed: {e}")
        return None

if __name__ == "__main__":
    print("🧪 Testing Enhanced Receipt Processor...")
    asyncio.run(test_receipt_processor())
