from fastapi import FastAPI
from .database import get_bag
from .models import Bag

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/reports/{id}", response_model=Bag)
def get_one(id: str):
    return get_bag(id)