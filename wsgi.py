from app import app

# The app object is imported directly
# Database initialization happens on first request via @app.before_first_request
# No need to manually initialize the database here

if __name__ == "__main__":
    app.run() 