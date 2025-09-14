"""
Database models for Scouter
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.dialects.sqlite import JSON
from typing import Optional, Dict, Any
import enum

db = SQLAlchemy()

# Enums for Receipt model
class ReceiptStatus(enum.Enum):
    """Receipt processing status"""
    UPLOADED = "uploaded"
    OCR_DONE = "ocr_done"
    AI_DONE = "ai_done"
    AI_LOW_CONFIDENCE = "ai_low_confidence"
    AWAITING_USER_REVIEW = "awaiting_user_review"
    VERIFIED = "verified"

class ReceiptSource(enum.Enum):
    """Receipt source/origin"""
    UPLOAD = "upload"
    MOBILE_SCAN = "mobile_scan"
    EMAIL = "email"

class Organization(db.Model):
    """Organization model"""
    __tablename__ = 'organizations'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="organization")
    
    def __repr__(self):
        return f'<Organization {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Organization relationship
    org_id: Mapped[int] = mapped_column(ForeignKey('organizations.id'), nullable=False)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    
    # Authentication fields
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_manager: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'name': self.name,
            'org_id': self.org_id,
            'organization': self.organization.name if self.organization else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_manager': self.is_manager,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_last_login(self):
        """Update the user's last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

class Receipt(db.Model):
    """Receipt model for storing processed receipt data"""
    __tablename__ = 'receipts'
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User relationship
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid'), nullable=False)
    user: Mapped["User"] = relationship("User", backref="receipts")
    
    # File storage info
    s3_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default=ReceiptSource.UPLOAD.value)
    
    # Core extracted receipt info
    receipt_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    amount_total: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    amount_subtotal: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    tax_amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, default="CAD")
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI & OCR data
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ReceiptStatus.UPLOADED.value)
    ocr_raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_review_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ai_confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    ai_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # State management
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Receipt {self.id} - {self.vendor_name} - ${self.amount_total}>'
    
    def to_dict(self):
        """Convert receipt to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            's3_url': self.s3_url,
            'filename': self.filename,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'source': self.source,
            'receipt_date': self.receipt_date.isoformat() if self.receipt_date else None,
            'amount_total': float(self.amount_total) if self.amount_total else None,
            'amount_subtotal': float(self.amount_subtotal) if self.amount_subtotal else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'currency': self.currency,
            'vendor_name': self.vendor_name,
            'location': self.location,
            'payment_method': self.payment_method,
            'category': self.category,
            'notes': self.notes,
            'status': self.status,
            'ocr_raw_text': self.ocr_raw_text,
            'ai_review_json': self.ai_review_json,
            'ai_confidence_score': float(self.ai_confidence_score) if self.ai_confidence_score else None,
            'ai_reviewed_at': self.ai_reviewed_at.isoformat() if self.ai_reviewed_at else None,
            'is_verified': self.is_verified,
            'is_archived': self.is_archived,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_from_ai_data(self, ai_data: Dict[str, Any], confidence_score: float):
        """Update receipt fields from AI processing results"""
        self.ai_review_json = ai_data
        self.ai_confidence_score = confidence_score
        self.ai_reviewed_at = datetime.utcnow()
        
        # Extract core fields from AI data
        if 'receipt_date' in ai_data and ai_data['receipt_date']:
            try:
                from datetime import datetime as dt
                self.receipt_date = dt.fromisoformat(ai_data['receipt_date']).date()
            except (ValueError, TypeError):
                pass
        
        if 'amount_total' in ai_data:
            self.amount_total = ai_data['amount_total']
        
        if 'amount_subtotal' in ai_data:
            self.amount_subtotal = ai_data['amount_subtotal']
            
        if 'tax_amount' in ai_data:
            self.tax_amount = ai_data['tax_amount']
            
        if 'currency' in ai_data:
            self.currency = ai_data['currency']
            
        if 'vendor_name' in ai_data:
            self.vendor_name = ai_data['vendor_name']
            
        if 'location' in ai_data:
            self.location = ai_data['location']
            
        if 'payment_method' in ai_data:
            self.payment_method = ai_data['payment_method']
            
        if 'category' in ai_data:
            self.category = ai_data['category']
        
        # Update status based on confidence
        if confidence_score >= 0.8:
            self.status = ReceiptStatus.AWAITING_USER_REVIEW.value
        else:
            self.status = ReceiptStatus.AI_LOW_CONFIDENCE.value
    
    def verify(self):
        """Mark receipt as verified by user"""
        self.is_verified = True
        self.status = ReceiptStatus.VERIFIED.value
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Archive the receipt"""
        self.is_archived = True
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """Soft delete the receipt"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow() 