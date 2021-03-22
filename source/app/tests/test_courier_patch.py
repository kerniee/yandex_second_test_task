from .test_db import *
from .utils import add_couriers


def test_patch_couriers_200():
    add_couriers(client, 10)
    json_data = {
        "regions": [123],
        "working_hours": ["12:34-23:45"],
        "courier_type": "foot"
    }
    response = client.patch(
        "/couriers/31",
        json=json_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "courier_id": 31,
        "courier_type": "foot",
        "regions": [123],
        "working_hours": ["12:34-23:45"]
    }


def test_patch_couriers_200_empty():
    json_data = {}
    response = client.patch(
        "/couriers/31",
        json=json_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "courier_id": 31,
        "courier_type": "foot",
        "regions": [123],
        "working_hours": ["12:34-23:45"]
    }


def test_patch_couriers_400():
    json_data = {
        "wrong_field": [123],
        "working_hours": []
    }
    response = client.patch(
        "/couriers/31",
        json=json_data,
    )
    assert response.status_code == 400
    data = response.json()
    assert data is None
