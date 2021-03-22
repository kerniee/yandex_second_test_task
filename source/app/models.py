from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Table
from sqlalchemy import Time as SQLTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import InstrumentedList

from .database import Base

courier_region = Table('association', Base.metadata,
                       Column('couriers_id', Integer, ForeignKey('couriers.id')),
                       Column('regions_id', Integer, ForeignKey('regions.id'))
                       )

courier_avrtime = Table('association2', Base.metadata,
                        Column('couriers_id', Integer, ForeignKey('couriers.id')),
                        Column('avr_time_id', Integer, ForeignKey('average_times.id'))
                        )

order_intervals = Table('association3', Base.metadata,
                        Column('orders_id', Integer, ForeignKey('orders.id')),
                        Column('intervals_id', Integer, ForeignKey('times.id'))
                        )

courier_intervals = Table('association4', Base.metadata,
                          Column('courier_id', Integer, ForeignKey('couriers.id')),
                          Column('intervals', Integer, ForeignKey('times.id'))
                          )


class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    regions = relationship("Region", secondary=courier_region)
    avg_times = relationship("AverageTime", secondary=courier_avrtime)
    intervals: InstrumentedList = relationship("Time", order_by="asc(Time.time_from)", secondary=courier_intervals)
    orders = relationship("Order")
    earnings = Column(Integer, default=0)
    last_order_time = Column(String)

    @hybrid_property
    def courier_id(self):
        return self.id

    @hybrid_property
    def courier_type(self):
        return self.type

    @hybrid_property
    def working_hours(self):
        s = []
        for interval in self.intervals:
            s.append(interval.time_from.strftime("%H:%M") + "-" + interval.time_to.strftime("%H:%M"))
        return s

    @hybrid_property
    def rating(self):
        t = min([s.avg_value for s in self.avg_times])
        # Straight copy-paste
        return (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float)
    region = Column(Integer, ForeignKey('regions.id'), nullable=False)
    regions = relationship("Region", foreign_keys=[region])
    intervals: InstrumentedList = relationship("Time", order_by="asc(Time.time_from)", secondary=order_intervals)

    @hybrid_property
    def delivery_hours(self):
        s = []
        for interval in self.intervals:
            s.append(interval.time_from.strftime("%H:%M") + "-" + interval.time_to.strftime("%H:%M"))
        return s

    finished = Column(Boolean, default=False)
    finished_time = Column(String)

    # courier = relationship("Courier", back_populates="orders")
    courier_id = Column(Integer, ForeignKey('couriers.id'))
    started_time = Column(String)


class AverageTime(Base):
    __tablename__ = "average_times"
    id = Column(Integer, primary_key=True)
    region_id = relationship("Region", uselist=False, back_populates="avr_time")
    avg_value = Column(Integer, default=0)
    num_of_orders = Column(Integer, default=0)


class Time(Base):
    __tablename__ = "times"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    time_from = Column(SQLTime)
    time_to = Column(SQLTime)

    courier_id = Column(Integer, ForeignKey('couriers.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))

    def __repr__(self):
        return f"<Time from {self.time_from} to {self.time_to}>"


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    courier_id = Column(Integer, ForeignKey('couriers.id'))
    order = Column(Integer, ForeignKey('orders.id'))
    avr_time_id = Column(Integer, ForeignKey('average_times.id'))
    avr_time = relationship("AverageTime", back_populates="region_id")

    def __int__(self):
        return self.id
