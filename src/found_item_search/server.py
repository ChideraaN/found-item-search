from fastapi import FastAPI, HTTPException
from .database import get_bag
from .models import Bag

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/reports/{report_id}", response_model=Bag)
def get_one(report_id: str):
    bag = get_bag(report_id)

    if bag is None:
        raise HTTPException(
            status_code=404,
            detail="Bag not found"
        )
    else:
        return bag
