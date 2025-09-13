#!/usr/bin/env python3
"""
Seed script to populate the database with test data
"""

from auth_server import app
from models import db, Organization, User

def seed_database():
    """Create test organizations and users"""
    with app.app_context():
        # Clear existing data
        User.query.delete()
        Organization.query.delete()
        
        # Create organizations
        org1 = Organization(name="Acme Corporation")
        org2 = Organization(name="Tech Innovations Inc")
        org3 = Organization(name="Green Energy Solutions")
        
        db.session.add_all([org1, org2, org3])
        db.session.commit()
        
        # Create users
        users = [
            # Acme Corporation users
            User(
                name="John Doe",
                email="john.doe@acme.com",
                org_id=org1.id
            ),
            User(
                name="Jane Smith",
                email="jane.smith@acme.com",
                org_id=org1.id
            ),
            
            # Tech Innovations Inc users
            User(
                name="Alice Johnson",
                email="alice.johnson@techinnovations.com",
                org_id=org2.id
            ),
            User(
                name="Bob Wilson",
                email="bob.wilson@techinnovations.com",
                org_id=org2.id
            ),
            
            # Green Energy Solutions users
            User(
                name="Carol Davis",
                email="carol.davis@greenenergy.com",
                org_id=org3.id
            ),
            User(
                name="David Brown",
                email="david.brown@greenenergy.com",
                org_id=org3.id
            )
        ]
        
        db.session.add_all(users)
        db.session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"Created {len([org1, org2, org3])} organizations:")
        for org in [org1, org2, org3]:
            print(f"  - {org.name} (UUID: {org.uuid})")
        
        print(f"\nCreated {len(users)} users:")
        for user in users:
            print(f"  - {user.name} ({user.email}) - {user.organization.name}")

if __name__ == "__main__":
    seed_database() 