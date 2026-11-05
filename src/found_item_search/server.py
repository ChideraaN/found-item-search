from fastapi import FastAPI, HTTPException
from .database import get_bag_report, create_bag_report
from .models import Bag

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/reports/{report_id}", response_model=Bag)
def get_one(report_id: str):
    bag = get_bag_report(report_id)

    if bag is None:
        raise HTTPException(
            status_code=404,
            detail="Bag not found"
        )
    else:
        return bag

@app.post("/reports", response_model=Bag, status_code=201)
def create_bag(bag: Bag):
    created_bag = create_bag_report(bag)
    if created_bag is None:
        raise HTTPException(
            status_code=409,
            detail="Bag with this report_id already exists"
        )
    return created_bag