import sys
import os
import time

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import engine, Base, SessionLocal
from app.models.user_model import SuperAdmin
from app.auth.token_utils import hash_password

def create_tables():
    print("Waiting for database connection...")
    max_retries = 10
    retry_count = 0
    connected = False
    
    while retry_count < max_retries and not connected:
        try:
            # Try to connect to the database
            with engine.connect() as connection:
                print("Database connection established.")
                connected = True
        except Exception as e:
            retry_count += 1
            print(f"Database not ready (attempt {retry_count}/{max_retries}). Waiting 5 seconds...")
            time.sleep(5)
            
    if not connected:
        print("Error: Could not connect to database after several attempts.")
        sys.exit(1)

    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
        # Seed initial admin if not exists
        db = SessionLocal()
        try:
            admin_exists = db.query(SuperAdmin).first()
            if not admin_exists:
                print("Seeding initial SuperAdmin...")
                initial_admin = SuperAdmin(
                    username="admin",
                    email="admin@edtech.com",
                    hashed_password=hash_password("admin123")
                )
                db.add(initial_admin)
                db.commit()
                print("SuperAdmin 'admin' created with password 'admin123'")
        finally:
            db.close()
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()
