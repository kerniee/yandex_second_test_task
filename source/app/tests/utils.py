import json

from ..schemas import OrderItem, CourierItem


def add_couriers(client, ids: int):
    json_data = {
        "data": [
            {
                "courier_id": 3 * ids + 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 3 * ids + 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3 * ids + 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            },
        ]
    }
    return client.post(
        "/couriers",
        json=json_data,
    )


# def add_courier(client, courier: CourierItem, full_add=False):
#     j = json.loads(courier.json())
#     if full_add:
#         client.post(
#             "/couriers",
#             json={"data": [j]},
#         )
#     return j


def add_orders(client, ids: int):
    json_data = {
        "data": [
            {
                "order_id": ids * 3 + 1,
                "weight": 0.21,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": ids * 3 + 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": ids * 3 + 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            },
        ]
    }
    return client.post(
        "/orders",
        json=json_data,
    )


def add_order(client, order: OrderItem, full_add=False):
    j = json.loads(order.json())
    if full_add:
        client.post(
            "/orders",
            json={"data": [j]},
        )
    return j


def add_courier(client, courier: CourierItem):
    json_data = {"data": [json.loads(courier.json())]}
    resp = client.post(
        "/couriers",
        json=json_data,
    )
    assert resp.status_code == 201
    return resp


def check_ids(client, arr, to_test):
    for i, key in enumerate(sorted(arr, key=lambda e: e["id"])):
        assert arr[i]["id"] == to_test[i]["id"]
