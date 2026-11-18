import psycopg
from psycopg.rows import dict_row
import pytest

def test_db_seed():
    with psycopg.connect() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT COUNT(*) FROM bag_reports")
            count = cur.fetchall()
            assert count[0]["count"] == 5

def test_get_bag_by_id(test_client):
    response = test_client.get("/reports/R-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == "R-1001"
    assert data["colour"] == "blue"
    assert data["bag_form"] == "backpack"
    assert data["shell"] == "soft"
    assert data["brand"] == "brand_a"
    assert data["weight_kg"] == 2.5

@pytest.mark.parametrize("brand, weight_kg", [
    ("brand_f", 1.5),
    (None,None)
])
def test_create_bag(test_client, brand, weight_kg):
    new_bag = {
        "report_id": "R-1006",
        "colour": "purple",
        "bag_form": "suitcase",
        "shell": "soft",
        "brand": brand,
        "weight_kg": weight_kg
    }

    response = test_client.post("/reports", json=new_bag)
    assert response.status_code == 201
    data = response.json()
    assert data["report_id"] == new_bag["report_id"]
    assert data["colour"] == new_bag["colour"]
    assert data["bag_form"] == new_bag["bag_form"]
    assert data["shell"] == new_bag["shell"]
    assert data["brand"] == new_bag["brand"]
    assert data["weight_kg"] == new_bag["weight_kg"]

    test_saved_response = test_client.get(f"/reports/{new_bag['report_id']}")
    assert test_saved_response.status_code == 200
    test_saved_data = test_saved_response.json()
    assert test_saved_data["report_id"] == new_bag["report_id"]
    assert test_saved_data["brand"] == new_bag["brand"]
    assert test_saved_data["weight_kg"] == new_bag["weight_kg"]


@pytest.mark.parametrize(
    "filters, expected_report_ids",
    [
        pytest.param({"colour": "blue"}, ["R-1001"], id="colour_blue"),
        pytest.param({"bag_form": "duffel"}, ["R-1002", "R-1005"], id="bag_form_duffel"),
        pytest.param({"shell": "soft"}, ["R-1001", "R-1003", "R-1005"], id="shell_soft"),
        pytest.param({"brand": "brand_c"}, ["R-1003"], id="brand_c"),
        pytest.param({"weight_kg": 2.5}, ["R-1001"], id="weight_kg_2.5"),
        pytest.param({"colour": "red", "bag_form": "duffel"}, ["R-1002"], id="colour_red_bag_form_duffel"),
        pytest.param({"colour": "green", "bag_form": "suitcase", "shell": "soft"}, ["R-1003"], id="colour_green_bag_form_suitcase_shell_soft"),
        pytest.param({"colour": "yellow", "bag_form": "backpack", "shell": "hard", "brand": "brand_d"}, ["R-1004"], id="colour_yellow_bag_form_backpack_shell_hard_brand_d"),
        pytest.param({"colour": "black", "bag_form": "duffel", "shell": "soft", "brand": "brand_e", "weight_kg": 2.2}, ["R-1005"], id="colour_black_bag_form_duffel_shell_soft_brand_e_weight_kg_2.2"),
        pytest.param({"nonsense": "value"}, ["R-1001", "R-1002", "R-1003", "R-1004", "R-1005"], id="nonsense_value"),
        pytest.param({"colour": "blue", "bag_form": "duffel"}, [], id="colour_blue_bag_form_duffel"),
    ]
)
def test_get_bags_with_filters(test_client, filters, expected_report_ids):
    query_params = "&".join([f"{k}={v}" for k, v in filters.items()])
    response = test_client.get(f"/reports?{query_params}")
    assert response.status_code == 200
    data = response.json()
    assert sorted([bag["report_id"] for bag in data]) == sorted(expected_report_ids)

def test_same_id_twice(test_client):
    new_bag = {
        "report_id": "R-1001",
        "colour": "purple",
        "bag_form": "suitcase",
        "shell": "soft",
        "brand": "brand_f",
        "weight_kg": 1.5
    }

    response = test_client.post("/reports", json=new_bag)
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Bag with this report_id already exists"

    test_existing_row_not_changed_response = test_client.get(f"/reports/{new_bag['report_id']}")
    assert test_existing_row_not_changed_response.status_code == 200
    test_existing_row_not_changed_data = test_existing_row_not_changed_response.json()
    assert test_existing_row_not_changed_data["colour"] == "blue"

def test_get_nonexistent_bag(test_client):
    response = test_client.get("/reports/R-9999")
    assert response.status_code == 404
    data = response.json() 
    assert data["detail"] == "Bag not found"

def test_bad_bag_form(test_client):
    new_bag = {
            "report_id": "R-1008",
            "colour": "purple",
            "bag_form": "banana",
            "shell": "soft",
            "brand": "brand_f",
            "weight_kg": 1.5
        }

    response = test_client.post("/reports", json=new_bag)
    assert response.status_code == 422

    check_not_in_db_response = test_client.get(f"/reports/{new_bag['report_id']}")
    assert check_not_in_db_response.status_code == 404

def test_get_invalid_bag_form(test_client):
    response = test_client.get("/reports?bag_form=banana")
    assert response.status_code == 422

def test_valid_limit_offset(test_client):
    response = test_client.get("/reports?limit=2&offset=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["report_id"] == "R-1002"
    assert data[1]["report_id"] == "R-1003"

def test_second_page_with_limit_offset(test_client):
    response = test_client.get("/reports?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["report_id"] == "R-1003"
    assert data[1]["report_id"] == "R-1004"

def test_zero_limit(test_client):
    response = test_client.get("/reports?limit=0")
    assert response.status_code == 422