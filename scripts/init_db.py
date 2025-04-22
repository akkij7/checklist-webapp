"""
Database initialization script for Render deployment.
Run this script on deployment to ensure the database is properly set up.
"""

import os
import sys
import traceback

# Ensure the data directory exists
if os.environ.get('RENDER'):
    DATA_DIR = '/data'
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            os.chmod(DATA_DIR, 0o777)
            print(f"Created data directory at {DATA_DIR}")
        except Exception as e:
            print(f"Error creating data directory: {e}")
            traceback.print_exc()
            sys.exit(1)

from app import app, db
from models import Checklist, ChecklistItem

def init_db():
    """Initialize the database tables."""
    print("Starting database initialization...")
    
    try:
        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Check if we have any checklists already
            checklist_count = Checklist.query.count()
            print(f"Found {checklist_count} existing checklists.")
            
            # Create a sample checklist if none exist
            if checklist_count == 0:
                print("Creating a sample checklist...")
                sample_checklist = Checklist(
                    name="Getting Started",
                    slug="getting-started"
                )
                db.session.add(sample_checklist)
                db.session.commit()
                
                # Add sample items
                sample_items = [
                    "Welcome to ChecklistPro!",
                    "Create your own checklist",
                    "Share the link with others",
                    "Check off completed items",
                    "Drag items to reorder them"
                ]
                
                for position, text in enumerate(sample_items):
                    item = ChecklistItem(
                        text=text,
                        checklist_id=sample_checklist.id,
                        position=position
                    )
                    db.session.add(item)
                
                db.session.commit()
                print("Sample checklist created successfully!")
            
            print("Database initialization complete!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_db()
    print("Script completed successfully!") 