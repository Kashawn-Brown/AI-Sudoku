# Import the FastAPI framework to create the API
from fastapi import FastAPI
# To allow CORS
from fastapi.middleware.cors import CORSMiddleware

# Import the routers (modules that handle different API endpoints)
# Import database and routers
from database import Base, engine
from routers import game, user, auth, board, gamesession

# Entry Point

# Create a FastAPI application instance with a title for documentation
app = FastAPI(title="Sudoku API")



# Include routers for different endpoints  
app.include_router(game.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(board.router)
app.include_router(gamesession.router)



# Define a simple root endpoint that returns a welcome message
@app.get("/") # Root endpoint 
def root():
    return {"message": "Welcome to the Sudoku API"}

# Specify the allowed origins
allowed_origins = [
    # "http://localhost:5173/",  # Replace with your frontend's URL
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all HTTP headers
)


# Create all tables in the database (Runs only once at startup)
# Create tables (only for development, in production use migrations)
Base.metadata.create_all(bind=engine)