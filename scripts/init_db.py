"""
Database initialization script for Render deployment.
Run this script on deployment to ensure the database is properly set up.
"""

from app import app, db
from models import Checklist, ChecklistItem

def init_db():
    """Initialize the database tables."""
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

if __name__ == "__main__":
    init_db() 