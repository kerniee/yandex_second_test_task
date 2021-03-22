from datetime import datetime

from .test_db import *
from .utils import add_courier, add_order
from ..schemas import OrderItem, CourierItem, CourierType
from ..utils import time_to_str


def test_post_orders_complete():
    add_order(client, OrderItem(
        order_id=12345,
        weight=1,
        region=1,
        delivery_hours=["00:00-23:59"]
    ), full_add=True)

    add_courier(client, CourierItem(
        courier_id=12345,
        courier_type=CourierType.bike,
        regions=[1],
        working_hours=["00:00-23:59"]
    ))

    json_data = {
        "courier_id": 12345,
        "order_id": 12345,
        "complete_time": time_to_str(datetime.now())
    }
    resp = client.post(
        "/orders/complete",
        json=json_data,
    )
    data = resp.json()
    assert resp.status_code == 400
    assert data is None

    json_data = {
        "courier_id": 12345
    }
    client.post(
        "/orders/assign",
        json=json_data,
    )

    json_data = {
        "courier_id": 12345,
        "order_id": 12345,
        "complete_time": time_to_str(datetime.now())
    }
    resp = client.post(
        "/orders/complete",
        json=json_data,
    )
    data = resp.json()
    assert resp.status_code == 200
    assert "order_id" in data


def test_post_orders_complete_empty():
    add_order(client, OrderItem(
        order_id=12346,
        weight=1,
        region=1,
        delivery_hours=["00:00-23:59"]
    ))
    add_courier(client, CourierItem(
        courier_id=12346,
        courier_type=CourierType.bike,
        regions=[1],
        working_hours=["00:00-23:59"]
    ))

    json_data = {
        "courier_id": 12346
    }
    client.post(
        "/orders/assign",
        json=json_data,
    )

    json_data_cases = [
        {
            "courier_id": 12346,
            "order_id": 999999,
            "complete_time": time_to_str(datetime.now())
        },
        {
            "courier_id": 999999,
            "order_id": 12346,
            "complete_time": time_to_str(datetime.now())
        },
        {
            "courier_id": 999999,
            "order_id": 999999,
            "complete_time": time_to_str(datetime.now())
        }
    ]
    for json_data in json_data_cases:
        resp = client.post(
            "/orders/complete",
            json=json_data,
        )
        data = resp.json()
        assert resp.status_code == 400
        assert data is None
