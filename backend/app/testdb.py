from database import SessionLocal, engine
import sqlalchemy

# Test database connection
try:
    # Check if the database engine connects successfully
    with engine.connect() as connection:
        print("✅ Successfully connected to the database!")

    # Test session creation
    db = SessionLocal()
    print("✅ Database session created successfully!")

    # Close session
    db.close()
    print("✅ Database session closed successfully!")

except sqlalchemy.exc.OperationalError as e:
    print("❌ Database connection failed!")
    print(f"Error: {e}")
