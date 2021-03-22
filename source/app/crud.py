import datetime
from typing import Union, List

from sqlalchemy.orm import Session

from . import models, schemas
from .utils import unpack_time, str_to_time


def create_simple_model(db, value, model, field_name: str, commit=True):
    db_model = db.query(model).filter(getattr(model, field_name) == value).first()
    if db_model is None:
        db_model = model(**{field_name: value})
        db.add(db_model)
        if commit:
            db.commit()
    return db_model


def create_region(db: Session, region: int) -> models.Region:
    return create_simple_model(db, region, models.Region, "id")


def create_time(db: Session, time_from: datetime.time, time_to: datetime.time, commit=True) -> models.Time:
    db_model = db.query(models.Time).filter(
        models.Time.time_from == time_from,
        models.Time.time_to == time_to,
    ).first()
    if db_model is None:
        db_model = models.Time(time_from=time_from, time_to=time_to)
        db.add(db_model)
        if commit:
            db.commit()
            db.refresh(db_model)
    return db_model


def create_order(db: Session, order: schemas.OrderItem, commit=True):
    intervals = unpack_time(order.delivery_hours)
    intervals = [create_time(db, t1, t2, commit=commit) for t1, t2 in intervals]

    db_order = models.Order(id=order.order_id,
                            weight=order.weight,
                            region=create_region(db, order.region).id,
                            intervals=intervals)
    db.add(db_order)
    if commit:
        db.commit()
    return db_order


def create_courier(db: Session, courier: schemas.CourierItem, commit=True):
    intervals = unpack_time(courier.working_hours)
    intervals = [create_time(db, t1, t2) for t1, t2 in intervals]

    db_courier = models.Courier(id=courier.courier_id,
                                type=courier.courier_type.value,
                                regions=[create_region(db, r) for r in courier.regions],
                                intervals=intervals)
    db.add(db_courier)
    if commit:
        db.commit()
    return db_courier


def create_average_time(db: Session,
                        courier: models.Courier,
                        region: models.Region,
                        commit=True):
    db_avr_time = create_simple_model(db, region, models.AverageTime, "region_id", False)
    # db_avr_time = db.query(models.AverageTime).filter(models.AverageTime.region_id == region.id).first()
    # if db_avr_time is None:
    #     db_avr_time = models.AverageTime(region_id=region.id)
    #     db.add(db_avr_time)
    if db_avr_time not in courier.avg_times:
        courier.avg_times.append(db_avr_time)
        db.add(courier)
        if commit:
            db.commit()
    return db_avr_time


def get_average_time(db: Session,
                     courier: models.Courier,
                     region: models.Region) -> models.AverageTime:
    for db_avr_time in courier.avg_times:
        if db_avr_time.region_id == region.id:
            return db_avr_time


def update_and_create_average_time(db: Session,
                                   courier: models.Courier,
                                   region: models.Region,
                                   new_time_diff: float,
                                   commit=True):
    avr_time = get_average_time(db, courier, region)
    if avr_time is None:
        avr_time = create_average_time(db, courier, region)
        # raise Exception("No such average value")

    t = avr_time.num_of_orders
    x = avr_time.avg_value * t
    new_avr_value = (x + new_time_diff) / (t + 1)

    avr_time.avg_value = new_avr_value
    avr_time.num_of_orders += 1

    db.add(avr_time)
    if commit:
        db.commit()


def update_courier(db: Session, courier_id: int, d: dict, commit=True):
    db_courier = get_courier(db, courier_id)
    if db_courier is None:
        return
    for key, value in d.items():
        if value is not None:
            # setattr(db_courier, key, value)
            if key == "regions":
                db_courier.regions = [create_region(db, r) for r in value]
            if key == "courier_type":
                db_courier.type = value.value
            if key == "working_hours":
                intervals = unpack_time(value)
                intervals = [create_time(db, t1, t2) for t1, t2 in intervals]
                db_courier.intervals = intervals
    db.add(db_courier)
    if commit:
        db.commit()
    return db_courier


def update_order_finished(db: Session, order: models.Order, finished_time: str):
    order.finished = True
    db_courier = get_courier(db, order.courier_id)
    db_region = get_region(db, order.region)
    if db_courier.last_order_time is None:
        new_time_diff = str_to_time(finished_time) - str_to_time(order.started_time)
    else:
        new_time_diff = str_to_time(finished_time) - str_to_time(db_courier.last_order_time)
    db_courier.last_order_time = finished_time
    update_and_create_average_time(db, courier=db_courier, region=db_region, new_time_diff=new_time_diff.seconds)
    # order.finished_time = time
    db.add(order)
    db.add(db_courier)
    db.commit()


def increment_earnings(db: Session, courier: models.Courier):
    courier.earnings += 500 * schemas.CourierType(courier.type).earning_coef()
    db.add(courier)
    db.commit()


def get_appropriate_orders(db: Session, courier: models.Courier) -> List[models.Order]:
    return db.query(models.Order).filter(models.Order.finished == False,
                                         models.Order.weight <= schemas.CourierType(courier.type).carry_cap(),
                                         models.Order.region.in_([s.id for s in courier.regions]))


def get_courier(db: Session, courier_id: int) -> Union[models.Courier, None]:
    return db.query(models.Courier).filter(models.Courier.id == courier_id).first()


def get_order(db: Session, order_id: int) -> Union[models.Order, None]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_region(db: Session, region_id: int):
    return db.query(models.Region).filter(models.Region.id == region_id).first()
