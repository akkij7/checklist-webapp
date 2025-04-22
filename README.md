# ChecklistApp

A simple web application built with Python (Flask) and Bootstrap for creating, managing, and sharing checklists online.

## Features

*   **Create Checklists:** Easily create new checklists with a title.
*   **Add Items:** Add items to your checklist individually or in bulk (comma or newline separated).
*   **Mark Items:** Mark items as complete or incomplete.
*   **Progress Tracking:** Visual progress bar shows completion status.
*   **Shareable Links:** Each checklist gets a unique, shareable link based on the checklist name.
*   **Clean URLs:** Human-readable URLs based on checklist names for easy sharing.
*   **Drag & Drop Reordering:** Easily rearrange your checklist items with intuitive drag and drop.
*   **Smart Item Formatting:** Automatic capitalization and period removal for consistent item display.
*   **Visual Feedback:** Subtle animations provide feedback when completing tasks.
*   **Keyboard Shortcuts:** Press 'c' on the homepage to quickly focus the checklist name field.
*   **Mobile Responsive:** Well-designed for all screen sizes.
*   **Modern UI:** Clean, beautiful interface with thoughtful user experience details.
*   **Delete Items/Lists:** Remove individual items or entire checklists.
*   **Clipboard Functionality:** Easily copy the shareable link.

## Setup and Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <your-repo-url> # Or download ZIP
    cd ChecklistWebsite # Navigate into the project directory
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    *   On Windows: `.\venv\Scripts\activate`
    *   On macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database and Apply Migrations:**
    Flask-Migrate is used to manage the database schema.

    *   **First time setup:** Initialize the migration environment:
        ```bash
        flask db init
        ```
        (This creates a `migrations` folder. You only need to run this once.)

    *   **Create initial migration:** Generate the script to create your tables based on the models:
        ```bash
        flask db migrate -m "Initial migration with Checklist and ChecklistItem tables."
        ```

    *   **Apply the migration:** Create the tables in the database:
        ```bash
        flask db upgrade
        ```

    *   **Future changes:** If you modify your models in `models.py` later, repeat the `migrate` and `upgrade` steps:
        ```bash
        flask db migrate -m "Description of changes made."
        flask db upgrade
        ```

## Running the Application

1.  **Start the Flask development server:**
    ```bash
    python app.py
    ```

2.  **Open your web browser** and navigate to:
    `http://127.0.0.1:5000` (or the address provided in the terminal)

## Project Structure

```
/ChecklistWebsite
|-- app.py             # Main Flask application file (routes, logic)
|-- models.py          # SQLAlchemy database models
|-- extensions.py      # SQLAlchemy and Migrate instances
|-- requirements.txt   # Python package dependencies
|-- checklist.db       # SQLite database file (created automatically)
|-- /migrations        # Flask-Migrate migration scripts (created by `flask db init`)
|-- /templates
|   |-- base.html      # Base HTML template (navbar, footer, etc.)
|   |-- index.html     # Homepage template (create checklist form)
|   |-- view_checklist.html # Template to display a specific checklist
|-- /static
|   |-- /css
|   |   |-- style.css  # Custom stylesheets
|   |-- /js
|   |   |-- script.js  # Custom JavaScript
|-- README.md          # This file
|-- venv/              # Virtual environment directory (optional)
```

## Deployment

*   **Secret Key:** For production, replace `app.config['SECRET_KEY'] = os.urandom(24)` in `app.py` with a static, securely generated secret key (e.g., using `secrets.token_hex(16)`).
*   **Debug Mode:** Ensure `debug=True` is set to `False` in `app.run()` for production.
*   **WSGI Server:** Use a production-ready WSGI server like Gunicorn or Waitress instead of Flask's built-in development server.
*   **Platform:** You mentioned wanting to host on a free platform other than Render. Options include:
    *   **PythonAnywhere:** Offers free tiers suitable for small Flask apps.
    *   **Fly.io:** Has a generous free tier, good for containerized apps.
    *   **Vercel:** Can deploy Python serverless functions (might require adapting the app structure).
    *   **Google Cloud Run / AWS App Runner:** Offer free tiers, but might be more complex to set up initially.
    *   **Heroku:** (While not strictly free anymore, has low-cost options that might work depending on usage).

    Each platform has specific deployment instructions. Consult their documentation for details.

## Deployment to Render

This repository is pre-configured for deployment on Render.

### Manual Deployment Steps

1. **Sign up for Render**
   - Create an account at [render.com](https://render.com)

2. **Create a New Web Service**
   - Click "New" and select "Web Service"
   - Select "Upload Files" (instead of connecting to a repository)

3. **Upload Your Project**
   - Compress your project folder into a ZIP file
   - Upload the ZIP file when prompted 

4. **Configure Your Service**
   - **Name**: Choose a name for your service
   - **Runtime**: Select Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. **Environment Variables**
   - Add `RENDER=true` to enable Render-specific configurations

6. **Persistent Disk**
   - Enable a persistent disk for your SQLite database
   - Set the path to `/data`
   - Choose at least 1GB of storage

7. **Initialize the Database**
   - After deployment, go to your service's "Shell" tab
   - Run: `python scripts/init_db.py`

8. **Access Your Application**
   - Visit the URL provided by Render

## Local Development

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Visit `http://localhost:5000` in your browser

## License

MIT 