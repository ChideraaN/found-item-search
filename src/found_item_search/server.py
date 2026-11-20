from fastapi import FastAPI, HTTPException, Query

from found_item_search.database import (
    create_bag_report,
    get_bag_report,
    get_bag_report_by_property,
)
from found_item_search.models import Bag, BagForm, BagShell

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/reports/{report_id}", response_model=Bag)
def get_one(report_id: str):
    bag = get_bag_report(report_id)

    if bag is None:
        raise HTTPException(status_code=404, detail="Bag not found")
    else:
        return bag


@app.post("/reports", response_model=Bag, status_code=201)
def create_bag(bag: Bag):
    created_bag = create_bag_report(bag)
    if created_bag is None:
        raise HTTPException(
            status_code=409, detail="Bag with this report_id already exists"
        )
    return created_bag


@app.get("/reports", response_model=list[Bag])
def get_bags(
    colour: str | None = None,
    bag_form: BagForm | None = None,
    shell: BagShell | None = None,
    brand: str | None = None,
    weight_kg: float | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0, le=1000),
):
    filters = {
        key: value
        for key, value in {
            "colour": colour,
            "bag_form": bag_form,
            "shell": shell,
            "brand": brand,
            "weight_kg": weight_kg,
        }.items()
        if value is not None
    }

    return get_bag_report_by_property(filters, limit, offset)
