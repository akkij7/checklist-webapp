import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from extensions import db # Import db from extensions
from flask_migrate import Migrate # Import Migrate
import re # For parsing item input
import datetime # Add this import
from sqlalchemy import inspect # Add this import
import traceback # Add this import
from werkzeug.exceptions import HTTPException  # Add this import

# --- Database Initialization (before app and model import) ---
# db = SQLAlchemy() <-- Removed

# --- Models (Import after db is defined but before app initialization needs them) ---
# models.py should only import 'db' from this file
# from models import Checklist, ChecklistItem # <-- REMOVE this top-level import

# --- App Configuration --- 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# For local development
DATABASE_PATH = os.path.join(BASE_DIR, 'checklist.db')
# For Render deployment
if os.environ.get('RENDER'):
    DATABASE_PATH = os.path.join('/data', 'checklist.db')

app = Flask(__name__)
# Use environment variable for SECRET_KEY in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize db with app ---
db.init_app(app) # Associate db with the configured app

# --- Initialize Flask-Migrate ---
migrate = Migrate(app, db) # Add this line

# --- Import Models (Now that db is associated with app) ---
from models import Checklist, ChecklistItem

# --- Add function to check and create tables ---
def ensure_tables_exist(app, db):
    """Ensure all tables defined in the models exist in the database."""
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"Current tables in database: {tables}")
        
        # Try using SQLAlchemy's built-in methods first
        try:
            # Always recreate tables for this version
            print("Recreating database tables to ensure schema compatibility...")
            
            # Safely drop tables if they exist
            db.drop_all()
            
            # Create tables for all models
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error using SQLAlchemy to create tables: {e}")
            print("Attempting to create tables with raw SQL...")
            
            # Fallback to raw SQL
            try:
                with db.engine.connect() as conn:
                    # Drop tables if they exist
                    conn.execute(db.text("DROP TABLE IF EXISTS checklist_item"))
                    conn.execute(db.text("DROP TABLE IF EXISTS checklist"))
                    conn.commit()
                    
                    # Create tables
                    conn.execute(db.text("""
                    CREATE TABLE checklist (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(150) NOT NULL,
                        slug VARCHAR(50) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """))
                    
                    conn.execute(db.text("""
                    CREATE TABLE checklist_item (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text VARCHAR(300) NOT NULL,
                        is_completed BOOLEAN NOT NULL DEFAULT 0,
                        position INTEGER NOT NULL DEFAULT 0,
                        checklist_id INTEGER NOT NULL,
                        FOREIGN KEY (checklist_id) REFERENCES checklist (id) ON DELETE CASCADE
                    )
                    """))
                    conn.commit()
                    print("Tables created successfully with raw SQL!")
            except Exception as sql_error:
                print(f"Error creating tables with raw SQL: {sql_error}")
                print("WARNING: Application may not function correctly without database tables!")

# --- Ensure database tables exist ---
ensure_tables_exist(app, db)

@app.context_processor
def inject_now():
    """Make the current year available to all templates."""
    return {'now': datetime.datetime.utcnow()}

@app.errorhandler(Exception)
def handle_error(e):
    """Global error handler to log exceptions"""
    error_traceback = traceback.format_exc()
    print(f"=== EXCEPTION CAUGHT ===\n{error_traceback}\n======================")
    
    if isinstance(e, HTTPException):
        return render_template('error.html', error=e), e.code
    
    # For non-HTTP exceptions, return a 500 error
    return render_template('error.html', error="An internal server error occurred."), 500

# --- Routes ---

@app.route('/')
def index():
    """Homepage: Show form to create a new checklist."""
    # No model needed here
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_checklist():
    """Create a new checklist."""
    print("=== Starting create_checklist function ===")
    try:
        # Get form data 
        name = request.form.get('checklist_name', '').strip()
        items_raw = request.form.get('checklist_items', '').strip()
        print(f"Form data received - Name: '{name}', Items: '{items_raw}'")

        if not name:
            print("Error: No checklist name provided")
            flash('Checklist name is required!', 'error')
            return redirect(url_for('index'))

        # Parse checklist items
        parsed_items = parse_items(items_raw)
        print(f"Parsed {len(parsed_items)} items: {parsed_items}")
        
        # Generate a unique slug from the name
        try:
            slug = generate_unique_slug(name, db.session)
            print(f"Generated slug: '{slug}'")
        except Exception as slug_error:
            print(f"Slug generation error: {slug_error}")
            # Use a simpler approach for the slug
            slug = f"checklist-{uuid.uuid4().hex[:8]}"
            print(f"Using fallback slug: {slug}")

        # Create the checklist
        print("Creating new checklist object...")
        new_checklist = Checklist(name=name, slug=slug)
        db.session.add(new_checklist)
        
        try:
            print("Committing checklist to database...")
            db.session.commit()
            print(f"Checklist created with ID: {new_checklist.id}")
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error creating checklist: {db_error}")
            # Last resort approach - try to execute raw SQL
            try:
                print("Attempting direct SQL insertion...")
                with db.engine.connect() as conn:
                    insert_stmt = db.text(f"INSERT INTO checklist (name, slug) VALUES (:name, :slug)")
                    result = conn.execute(insert_stmt, {"name": name, "slug": slug})
                    conn.commit()
                    print("Direct SQL insertion succeeded")
                    # Get the inserted ID
                    select_stmt = db.text(f"SELECT id FROM checklist WHERE slug = :slug")
                    result = conn.execute(select_stmt, {"slug": slug})
                    checklist_id = result.fetchone()[0]
                    print(f"Retrieved checklist ID: {checklist_id}")
                    new_checklist.id = checklist_id
            except Exception as sql_error:
                print(f"Direct SQL insertion failed: {sql_error}")
                flash(f'Could not create checklist. Please try again.', 'error')
                return redirect(url_for('index'))

        # Add items if any were provided
        if parsed_items:
            print(f"Adding {len(parsed_items)} items to checklist...")
            for position, item_text in enumerate(parsed_items):
                try:
                    item = ChecklistItem(text=item_text, checklist_id=new_checklist.id, position=position)
                    db.session.add(item)
                    db.session.commit()
                    print(f"Added item: {item_text}")
                except Exception as item_error:
                    print(f"Error adding item '{item_text}': {item_error}")
                    db.session.rollback()
                    # Continue with other items

        print("Checklist creation successful, redirecting...")
        flash(f'Checklist "{name}" created successfully!', 'success')
        return redirect(url_for('view_checklist', slug=new_checklist.slug))
    except Exception as unexpected_error:
        print(f"Unexpected error in create_checklist: {unexpected_error}")
        traceback.print_exc()  # Print full stack trace
        flash(f'An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/create_ajax', methods=['POST'])
def create_checklist_ajax():
    """Create a new checklist with AJAX response."""
    response = {"status": "error", "message": "An unknown error occurred"}
    
    try:
        print("=== Starting create_checklist_ajax function ===")
        name = request.json.get('checklist_name', '').strip()
        items_raw = request.json.get('checklist_items', '').strip()
        print(f"JSON data received - Name: '{name}', Items: '{items_raw}'")

        if not name:
            response["message"] = "Checklist name is required!"
            return jsonify(response), 400

        parsed_items = parse_items(items_raw)
        print(f"Parsed {len(parsed_items)} items: {parsed_items}")
        
        # Generate a unique slug from the name
        try:
            slug = generate_unique_slug(name, db.session)
            print(f"Generated slug: '{slug}'")
        except Exception as slug_error:
            print(f"Slug generation error: {slug_error}")
            response["message"] = f"Error creating slug: {slug_error}"
            return jsonify(response), 500

        print("Creating new checklist object...")
        new_checklist = Checklist(name=name, slug=slug)
        db.session.add(new_checklist)
        
        try:
            print("Committing checklist to database...")
            db.session.commit()
            print(f"Checklist created with ID: {new_checklist.id}")
        except Exception as e:
            db.session.rollback()
            print(f"Database error creating checklist: {e}")
            response["message"] = f"Error creating checklist: {e}"
            return jsonify(response), 500

        # Add items if any were provided
        if parsed_items:
            print(f"Adding {len(parsed_items)} items to checklist...")
            for position, item_text in enumerate(parsed_items):
                item = ChecklistItem(text=item_text, checklist_id=new_checklist.id, position=position)
                db.session.add(item)
            try:
                print("Committing items to database...")
                db.session.commit()
                print("Items added successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Database error adding items: {e}")
                # Attempt to delete the checklist if items failed to add
                try:
                    db.session.delete(new_checklist)
                    db.session.commit()
                except:
                    pass  # If this also fails, just continue
                response["message"] = f"Error adding items: {e}"
                return jsonify(response), 500

        print("Checklist creation successful")
        response["status"] = "success"
        response["message"] = f"Checklist '{name}' created successfully!"
        response["redirect"] = url_for('view_checklist', slug=new_checklist.slug)
        return jsonify(response)
    except Exception as unexpected_error:
        print(f"Unexpected error in create_checklist_ajax: {unexpected_error}")
        traceback.print_exc()
        response["message"] = f"An unexpected error occurred: {unexpected_error}"
        return jsonify(response), 500

@app.route('/list/<string:slug>')
def view_checklist(slug):
    """Display a specific checklist."""
    checklist = Checklist.query.filter_by(slug=slug).first()
    if not checklist:
        abort(404)

    # Sort items by position
    items = sorted(checklist.items, key=lambda item: item.position)
    
    # Calculate progress
    total_items = len(items)
    completed_items = sum(1 for item in items if item.is_completed)
    progress = int((completed_items / total_items) * 100) if total_items > 0 else 0

    return render_template('view_checklist.html', checklist=checklist, items=items, progress=progress)

@app.route('/list/<string:slug>/add', methods=['POST'])
def add_item(slug):
    """Add items to a checklist."""
    checklist = Checklist.query.filter_by(slug=slug).first_or_404()
    items_raw = request.form.get('new_items', '').strip()

    if not items_raw:
        flash('No items provided to add.', 'warning')
        return redirect(url_for('view_checklist', slug=slug))

    parsed_items = parse_items(items_raw)
    if not parsed_items:
        flash('Could not parse any valid items.', 'warning')
        return redirect(url_for('view_checklist', slug=slug))

    # Get the highest position value
    max_position = db.session.query(db.func.max(ChecklistItem.position)).filter_by(checklist_id=checklist.id).scalar() or 0
    
    for i, item_text in enumerate(parsed_items):
        item = ChecklistItem(
            text=item_text, 
            checklist_id=checklist.id,
            position=max_position + i + 1
        )
        db.session.add(item)

    try:
        db.session.commit()
        flash(f'{len(parsed_items)} item(s) added.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding items: {e}', 'error')

    return redirect(url_for('view_checklist', slug=slug))

@app.route('/list/<string:slug>/toggle/<int:item_id>', methods=['POST'])
def toggle_item(slug, item_id):
    """Toggle the status of a checklist item."""
    checklist = Checklist.query.filter_by(slug=slug).first_or_404()
    item = ChecklistItem.query.filter_by(id=item_id, checklist_id=checklist.id).first_or_404()

    item.is_completed = not item.is_completed
    try:
        db.session.commit()
        
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Calculate updated progress
            items = ChecklistItem.query.filter_by(checklist_id=checklist.id).all()
            total_items = len(items)
            completed_items = sum(1 for item in items if item.is_completed)
            progress = int((completed_items / total_items) * 100) if total_items > 0 else 0
            
            return jsonify({
                'status': 'success',
                'item_id': item_id,
                'is_completed': item.is_completed,
                'progress': progress
            })
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating item status: {e}', 'error')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'error',
                'message': f'Error updating item: {e}'
            }), 500

    # For non-AJAX requests, redirect back to the checklist page
    return redirect(url_for('view_checklist', slug=slug))

@app.route('/list/<string:slug>/delete_item/<int:item_id>', methods=['POST'])
def delete_item(slug, item_id):
    """Delete an item from a checklist."""
    checklist = Checklist.query.filter_by(slug=slug).first_or_404()
    item = ChecklistItem.query.filter_by(id=item_id, checklist_id=checklist.id).first_or_404()

    db.session.delete(item)
    try:
        db.session.commit()
        flash('Item deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting item: {e}', 'error')

    return redirect(url_for('view_checklist', slug=slug))

@app.route('/list/<string:slug>/delete', methods=['POST'])
def delete_checklist(slug):
    """Delete an entire checklist."""
    checklist = Checklist.query.filter_by(slug=slug).first_or_404()
    checklist_name = checklist.name

    db.session.delete(checklist)
    try:
        db.session.commit()
        flash(f'Checklist "{checklist_name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting checklist: {e}', 'error')
        return redirect(url_for('view_checklist', slug=slug))

    return redirect(url_for('index'))

# --- Reordering items ---
@app.route('/list/<string:slug>/reorder', methods=['POST'])
def reorder_items(slug):
    """Reorder items in a checklist."""
    checklist = Checklist.query.filter_by(slug=slug).first_or_404()
    item_order = request.json.get('items', [])
    
    if not item_order:
        return jsonify({'status': 'error', 'message': 'No item order provided'}), 400
    
    try:
        # Update position for each item
        for position, item_id in enumerate(item_order):
            item = ChecklistItem.query.filter_by(id=item_id, checklist_id=checklist.id).first()
            if item:
                item.position = position
        
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Helper Functions ---

def clean_item_text(text):
    """Clean item text by removing trailing periods and extra whitespace."""
    text = text.strip()
    # Remove trailing period if present
    if text.endswith('.'):
        text = text[:-1]
    # Capitalize first letter if the text is long enough
    if len(text) > 0:
        text = text[0].upper() + text[1:]
    return text

def parse_items(item_string):
    """Parses a string containing items separated by commas or newlines."""
    if not item_string:
        return []
    # Split by one or more commas or newlines, strip whitespace, filter empty strings
    items = [clean_item_text(item.strip()) for item in re.split(r'[,\n]+', item_string) if item.strip()]
    return items

def generate_unique_slug(name, db_session):
    """Generates a unique slug based on the checklist name."""
    print(f"Generating slug for name: '{name}'")
    try:
        from models import Checklist, generate_slug
        
        # Generate base slug
        base_slug = generate_slug(name)
        print(f"Base slug generated: '{base_slug}'")
        
        # Handle empty slugs (in case name contains only non-alphanumeric chars)
        if not base_slug:
            base_slug = 'checklist'
            print("Empty slug detected, using default: 'checklist'")
        
        # Check if slug exists
        slug = base_slug
        count = 1
        
        while True:
            print(f"Checking if slug '{slug}' exists...")
            existing = db_session.query(Checklist).filter_by(slug=slug).first()
            if existing is None:
                print(f"Slug '{slug}' is available")
                break
            print(f"Slug '{slug}' already exists, trying with counter")
            slug = f"{base_slug}-{count}"
            count += 1
            # Prevent infinite loops
            if count > 100:
                print("Warning: Breaking slug generation loop after 100 attempts")
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
                break
        
        return slug
    except Exception as e:
        print(f"Error in generate_unique_slug: {e}")
        # Return a completely random slug as fallback
        random_slug = f"checklist-{uuid.uuid4().hex[:8]}"
        print(f"Returning random fallback slug: {random_slug}")
        return random_slug

# --- Initialize Database ---
# Use Flask CLI or a one-time script to create tables
# Example: flask shell -> from app import db -> db.create_all()

if __name__ == '__main__':
    # --- Remove old DB creation logic --- 
    # if not os.path.exists(DATABASE_PATH):
    #     with app.app_context(): 
    #         print("Creating database tables...")
    #         db.create_all()
    #         print("Database created!")
    # --- End Removal --- 

    app.run(debug=True) 