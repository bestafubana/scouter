"""
Database models for Scouter
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

db = SQLAlchemy()

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