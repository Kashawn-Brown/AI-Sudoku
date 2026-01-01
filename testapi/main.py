from fastapi import FastAPI, HTTPException
import boards
import random, requests

# To allow CORS
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

# To allow CORS (this allows from everywhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Default endpoint
@app.get('/')
async def root():
    return {"message": "This is an example", "data": 4}




# Sudoku stuff

# Modularizing API endpoints pertaining to the board (boards.py will handle board related endpoints)
app.include_router(boards.router)

@app.get('/sudoku')
async def sudoku():
    request = requests.get("https://sudoku-api.vercel.app/api/dosuku?query={newboard(limit:5){grids{value,solution,difficulty},results,message}}")
    return request.json()

@app.get('/sudoku/{limit}')
async def sudoku(limit):
    url = "https://sudoku-api.vercel.app/api/dosuku?query={newboard(limit:" + limit + "){grids{value,solution,difficulty},results,message}}"
    request = requests.get(url)
    return request.json()







# Random number example

# new endpoint
@app.get('/random')
async def get_random():
    rn: int = random.randint(0, 100)
    return {'number': rn, 'limit': 100}

# endpoint with a parameter
@app.get('/random/{limit}')
async def get_random(limit: int):
    rn: int = random.randint(0, limit)
    return {'number': rn, 'limit': limit}
""" 
    rn: int = __
    - type hinting: tells Python (and FastAPI) that rn should be an integer
    * just for clarity (same thing with limit parameter)
"""









# Items example

# items list
# could be good for something like notes app
items = []
# endpoint to add an item, to a list
@app.post('/items')
def create_item(item: str):
    if item not in items:
        items.append(item)
        return items
    else:
        raise HTTPException(status_code = 409, detail = f"{item} already in list")
# To add: http://127.0.0.1:8000/items?item=apple


# endpoint to retrieve all items currently in our items list
@app.get('/items')
def list_items():
    if not items:
        return {'message': 'The list is empty'}
    return items


# endpoint to get an item at a specified index using a variable in url
@app.get('/items/{item_id}')
def get_item(item_id: int) -> str:
    if item_id > -1 and item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


# endpoint to remove an item from our items list
@app.delete('/items')
def remove_item(item: str):
    if item in items:
        items.remove(item)
        return items
    else:
        raise HTTPException(status_code=404, detail=f"Item could not be removed. There is no {item} currently in the list")
# To delete: http://127.0.0.1:8000/items?item=apple