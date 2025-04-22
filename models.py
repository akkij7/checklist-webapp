from extensions import db
import re
from datetime import datetime

def generate_slug(text):
    """Generate a URL-friendly slug from text."""
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Limit length
    slug = slug[:50]
    return slug

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)  # Changed from link_id to slug
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add creation timestamp
    items = db.relationship('ChecklistItem', backref='checklist', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Checklist {self.name} ({self.slug})>'

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, default=0)  # Add position for ordering
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklist.id'), nullable=False)

    def __repr__(self):
        return f'<ChecklistItem {self.text[:20]}...>' 