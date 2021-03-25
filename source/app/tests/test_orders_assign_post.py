import datetime

from .test_db import *
from .utils import add_courier, add_order
from ..schemas import CourierItem, OrderItem, CourierType


def test_post_orders_assign():
    add_courier(client, CourierItem(
        courier_id=60,
        courier_type=CourierType.bike,
        regions=[123, 500, 999],
        working_hours=["10:00-12:00", "20:00-22:00"]
    ))
    json_data = {"data": []}
    for i in range(47):
        time = datetime.time(
            hour=i // 2,
            minute=(i % 2) * 30,
        )
        time2 = datetime.time(
            hour=(i + 1) // 2,
            minute=((i + 1) % 2) * 30,
        )
        json = add_order(client, OrderItem(
            order_id=500 + i,
            weight=1,
            region=500,
            delivery_hours=[
                time.strftime("%H:%M") + "-" +
                time2.strftime("%H:%M")]
        ))
        json_data["data"].append(json)
    resp = client.post(
        "/orders",
        json=json_data,
    )
    assert resp.status_code == 201

    json_data = {
        "courier_id": 60
    }
    for i in range(3):
        # test few times
        resp = client.post(
            "/orders/assign",
            json=json_data,
        )
        data = resp.json()
        assert 'orders' in data
        assert data["orders"] == [
            {'id': 519}, {'id': 520}, {'id': 521}, {'id': 522}, {'id': 523}, {'id': 524},
            {'id': 539}, {'id': 540}, {'id': 541}, {'id': 542}, {'id': 543}, {'id': 544}
        ]
        assert 'assign_time' in data
        assert data["assign_time"].startswith("2021-")


def test_post_orders_assign_weight_restriction():
    add_courier(client, CourierItem(
        courier_id=61,
        courier_type=CourierType.bike,
        regions=[123, 501, 999],
        working_hours=["00:00-23:50"]
    ))
    json_data = {"data": []}
    for i in range(47):
        time = datetime.time(
            hour=i // 2,
            minute=(i % 2) * 30,
        )
        time2 = datetime.time(
            hour=(i + 1) // 2,
            minute=((i + 1) % 2) * 30,
        )
        json = add_order(client, OrderItem(
            order_id=550 + i,
            weight=i + 1,
            region=501,
            delivery_hours=[
                time.strftime("%H:%M") + "-" +
                time2.strftime("%H:%M")]
        ))
        json_data["data"].append(json)
    resp = client.post(
        "/orders",
        json=json_data,
    )
    assert resp.status_code == 201

    json_data = {
        "courier_id": 61
    }
    for i in range(3):
        # test few times
        resp = client.post(
            "/orders/assign",
            json=json_data,
        )
        data = resp.json()
        assert 'orders' in data
        assert data["orders"] == [{'id': 550}, {'id': 551}, {'id': 552}, {'id': 553}, {'id': 554},
                                  {'id': 555}, {'id': 556}, {'id': 557}, {'id': 558}, {'id': 559},
                                  {'id': 560}, {'id': 561}, {'id': 562}, {'id': 563}, {'id': 564}]
        assert 'assign_time' in data
    # assert data["assign_time"].startswith("2021-")


def test_post_orders_assign_empty():
    add_courier(client, CourierItem(
        courier_id=62,
        courier_type=CourierType.bike,
        regions=[-1],
        working_hours=["23:58-23:59"]
    ))
    json_data = {"data": []}
    for i in range(47):
        time = datetime.time(
            hour=i // 2,
            minute=(i % 2) * 30,
        )
        time2 = datetime.time(
            hour=(i + 1) // 2,
            minute=((i + 1) % 2) * 30,
        )
        json = add_order(client, OrderItem(
            order_id=600 + i,
            weight=i + 1,
            region=501,
            delivery_hours=[
                time.strftime("%H:%M") + "-" +
                time2.strftime("%H:%M")]
        ))
        json_data["data"].append(json)
    resp = client.post(
        "/orders",
        json=json_data,
    )
    assert resp.status_code == 201

    json_data = {
        "courier_id": 62
    }
    for i in range(3):
        # test few times
        resp = client.post(
            "/orders/assign",
            json=json_data,
        )
        data = resp.json()
        assert data == {"orders": []}
        assert resp.status_code == 200


def test_post_orders_assign_invalid_courier():
    json_data = {
        "courier_id": 1234554321
    }
    for i in range(3):
        # test few times
        resp = client.post(
            "/orders/assign",
            json=json_data,
        )
        data = resp.json()
        assert data is None
        assert resp.status_code == 400
