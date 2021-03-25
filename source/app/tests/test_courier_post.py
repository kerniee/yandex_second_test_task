from .test_db import *
from .utils import add_couriers, check_ids


def test_post_couriers():
    response = add_couriers(client, 0)
    assert response.status_code == 201
    data = response.json()
    valid_data = {
        "couriers": [{"id": 1}, {"id": 2}, {"id": 3}]
    }
    assert data == valid_data


def test_wrong_post_couriers_spare_field():
    json_data = {
        "data": [
            {
                "courier_id": 11,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 102,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"],
                "foo": 'bar'
            },
            {
                "courier_id": 13,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 104,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"],
                "foo": 'bar'
            },
            {
                "courier_id": 105,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"],
                "foo": 'bar'
            },
        ]
    }
    response = client.post(
        "/couriers",
        json=json_data,
    )
    assert response.status_code == 400
    data = response.json()
    to_test = [{"id": 102}, {"id": 104}, {"id": 105}]
    check_ids(client, data["validation_error"]["couriers"], to_test)


def test_wrong_post_couriers_missing_field():
    json_data = {
        "data": [
            {
                "courier_id": 999,
                "courier_type": "foot",
                "regions": [1, 12, 22],
            },
            {
                "courier_id": 5,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
        ]
    }
    response = client.post(
        "/couriers",
        json=json_data,
    )
    assert response.status_code == 400
    data = response.json()
    to_test = [{"id": 999}]
    check_ids(client, data["validation_error"]["couriers"], to_test)
