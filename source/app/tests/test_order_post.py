from .test_db import *
from .utils import add_orders


def test_post_orders():
    response = add_orders(client, 0)
    assert response.status_code == 201
    data = response.json()
    valid_data = {
        "orders": [{"id": 1}, {"id": 2}, {"id": 3}]
    }
    assert data == valid_data


def test_wrong_post_orders_spare_field():
    json_data = {
        "data": [
            {
                "order_id": 11,
                "weight": 0.21,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 101,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"],
                "foo": "bar"
            },
            {
                "order_id": 12,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            },
            {
                "order_id": 102,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"],
                "foo": "bar"
            },
            {
                "order_id": 103,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"],
                "foo": "bar"
            },
        ]
    }
    response = client.post(
        "/orders",
        json=json_data,
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {
        "validation_error": {
            "orders": [{"id": 101}, {"id": 102}, {"id": 103}]
        }
    }


def test_wrong_post_orders_missing_field():
    json_data = {
        "data": [
            {
                "order_id": 999,
                "weight": 0.23,
                "region": 12,
            },
            {
                "order_id": 4,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 9999,
                "weight": 0.01,
                "region": 22,
            },
        ]
    }
    response = client.post(
        "/orders",
        json=json_data,
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {
        "validation_error": {
            "orders": [{"id": 999}, {"id": 9999}]
        }
    }
