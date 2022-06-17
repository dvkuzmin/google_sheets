from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    Date
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Order(Base):

    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_number = Column(Integer, nullable=False)
    price_usd = Column(Float, nullable=False)
    price_rub = Column(Float, nullable=False)
    delivery_date = Column(Date)

    def __repr__(self):
        return f"{self.order_number}, {self.price_usd}, {self.price_rub}, {self.delivery_date}"
