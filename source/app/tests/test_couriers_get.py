from datetime import datetime

from .test_db import *
from .utils import add_courier, add_order
from ..schemas import OrderItem, CourierItem, CourierType
from ..utils import time_to_str


def test_get_couriers_courier_id(num_of_orders=10):
    add_courier(client, CourierItem(
        courier_id=701,
        courier_type=CourierType.car,
        regions=[701],
        working_hours=["00:00-23:59"]
    ))  # 701 courier get created
    for i in range(num_of_orders):
        add_order(client, OrderItem(
            order_id=701 + i,
            weight=1,
            region=701,
            delivery_hours=["00:00-23:59"]
        ), full_add=True)
    resp = client.post(
        "/orders/assign",
        json={
            "courier_id": 701
        },
    )
    data = resp.json()
    resp = client.get(
        "/couriers/701"
    )
    data = resp.json()
    assert data == {'courier_id': 701,
                    'courier_type': 'car',
                    'regions': [701],
                    'working_hours': ['00:00-23:59'],
                    'rating': None,
                    'earnings': 0}
    for i in range(num_of_orders - 1):
        json_data = {
            "courier_id": 701,
            "order_id": 701 + i,
            "complete_time": time_to_str(datetime.now())
        }
        resp = client.post(
            "/orders/complete",
            json=json_data,
        )
        resp = client.get(
            "/couriers/701"
        )
        data = resp.json()
        assert data["earnings"] == 4500 * (i + 1)

    json_data = {
        "courier_type": "foot"
    }
    resp = client.patch(
        "/couriers/701",
        json=json_data,
    )
    assert resp.status_code == 200

    json_data = {
        "courier_id": 701,
        "order_id": 701 + num_of_orders - 1,
        "complete_time": time_to_str(datetime.now())
    }
    resp = client.post(
        "/orders/complete",
        json=json_data,
    )
    resp = client.get(
        "/couriers/701"
    )
    data = resp.json()
    assert data["earnings"] == 4500 * 9 + 1000

    resp = client.get(
        "/couriers/701"
    )
    data = resp.json()
    # assert data == {'courier_id': 12345,
    #                 'courier_type': 'bike',
    #                 'regions': [1],
    #                 'working_hours': [],
    #                 'rating': 5.0,
    #                 'earnings': 2500}
