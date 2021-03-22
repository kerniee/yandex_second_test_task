# generated by fastapi-codegen:
#   filename:  openapi.yaml
#   timestamp: 2021-03-11T13:33:03+00:00

import datetime
import re
from typing import Any, Union

import uvicorn
from fastapi import Depends, FastAPI, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.utils import time_to_str
from . import crud, models
from .database import SessionLocal, engine
from .schemas import (
    CourierGetResponse,
    CourierItem,
    CouriersIds,
    Courier,
    CouriersPostRequest,
    CourierUpdateRequest,
    OrdersAssignPostRequest,
    OrdersCompletePostRequest,
    OrdersCompletePostResponse,
    OrdersIds,
    Order,
    OrdersPostRequest,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title='Candy Delivery App',
    version='1.0',
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/couriers', response_model=CouriersIds, status_code=201)
def post_couriers(
        body: CouriersPostRequest = None,
        db: Session = Depends(get_db)
) -> CouriersIds:
    ids = []
    for courier in body.data:
        courier_model = crud.create_courier(db, courier)
        ids.append(Courier(id=courier_model.id))
    return CouriersIds(couriers=ids)


@app.patch('/couriers/{courier_id}', response_model=CourierItem)
def patch_couriers_courier_id(
        resp: Response,
        courier_id: int,
        body: CourierUpdateRequest = None,
        db: Session = Depends(get_db)
) -> Union[CourierItem, None]:
    db_courier = crud.update_courier(db, courier_id, body.dict())
    if db_courier is None:
        resp.status_code = 400
        return
    return db_courier


@app.post('/orders', response_model=OrdersIds, status_code=201)
def post_orders(
        body: OrdersPostRequest = None,
        db: Session = Depends(get_db)
) -> OrdersIds:
    ids = []
    for order in body.data:
        order_model = crud.create_order(db, order, commit=False)
        ids.append(Order(id=order_model.id))
    db.commit()
    return OrdersIds(orders=ids)


@app.post('/orders/assign', response_model=Any)
def post_orders_assign(
        resp: Response,
        body: OrdersAssignPostRequest = None,
        db: Session = Depends(get_db)
) -> Any:
    db_courier = crud.get_courier(db, body.courier_id)
    db_orders = crud.get_appropriate_orders(db, db_courier)
    if db_courier is None:
        resp.status_code = 400
        return
    assigned_orders = []
    time = datetime.datetime.now()
    time_formatted = time_to_str(time)
    for order in db_orders:
        order_i, courier_i = 0, 0
        while order_i < len(order.intervals) and courier_i < len(db_courier.intervals):
            order_interval = order.intervals[order_i]
            courier_interval = db_courier.intervals[courier_i]
            if order_interval.time_from < courier_interval.time_from:
                left = order_interval
                right = courier_interval
                order_i += 1
            else:
                left = courier_interval
                right = order_interval
                courier_i += 1
            if left.time_to >= right.time_from:
                # intersection
                if order.courier_id is None or order.courier_id == db_courier.id:
                    order.courier_id = db_courier.id
                    order.started_time = time_formatted
                    db.add(order)
                    # db.refresh(order)
                    assigned_orders.append({"id": order.id})
                    break
    # DEBUG: [db.query(models.Order).filter(models.Order.id == s["id"]).first().intervals for s in assigned_orders]
    db.commit()
    if len(assigned_orders) == 0:
        resp.status_code = 400
        return
    else:
        return {
            "orders": assigned_orders,
            "assign_time": time_formatted
        }


@app.post('/orders/complete', response_model=OrdersCompletePostResponse, status_code=200)
def post_orders_complete(
        resp: Response,
        body: OrdersCompletePostRequest = None,
        db: Session = Depends(get_db),
) -> Union[OrdersCompletePostResponse, None]:
    db_order = crud.get_order(db, body.order_id)
    if db_order is not None and db_order.courier_id == body.courier_id:
        crud.update_order_finished(db, db_order, body.complete_time)
        crud.increment_earnings(db, crud.get_courier(db, body.courier_id))
        return OrdersCompletePostResponse(order_id=body.order_id)
    resp.status_code = 400
    return


@app.get('/couriers/{courier_id}', response_model=CourierGetResponse)
def get_couriers_courier_id(
        courier_id: int,
        db: Session = Depends(get_db),
) -> CourierGetResponse:
    db_courier = crud.get_courier(db, courier_id)
    if db_courier.last_order_time is None:
        resp = CourierGetResponse(
            courier_id=courier_id,
            courier_type=db_courier.courier_type,
            regions=db_courier.regions,
            working_hours=db_courier.working_hours,
            earnings=db_courier.earnings
        )
    else:
        resp = db_courier
    return resp


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    content = {"detail": jsonable_encoder(exc.errors())}
    path = request.scope["path"]
    try:
        if path == "/couriers":
            wrong_ids = []
            for d in content["detail"]:
                arr_id = d["loc"][2]
                courier_id = exc.body["data"][arr_id]["courier_id"]
                wrong_ids.append({"id": courier_id})
            content = {"validation_error": {"couriers": wrong_ids}}
        elif re.match(r"/couriers/[0-9]+$", path):
            content = None
        elif path == "/orders":
            wrong_ids = []
            for d in content["detail"]:
                arr_id = d["loc"][2]
                order_id = exc.body["data"][arr_id]["order_id"]
                wrong_ids.append({"id": order_id})
            content = {"validation_error": {"orders": wrong_ids}}
    except Exception as e:
        content = {"detail": jsonable_encoder(exc.errors())}

    return JSONResponse(
        status_code=400,
        content=content,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)