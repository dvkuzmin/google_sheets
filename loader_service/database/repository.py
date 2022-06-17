from datetime import datetime

from .tables import Order
from dataclasses import dataclass
from sqlalchemy.orm.session import sessionmaker


@dataclass
class OrdersRepo:
    session_local: sessionmaker

    def get_all(self):
        with self.session_local() as sess:
            return sess.query(Order).all()

    def get_by_id(self, order_id: int) -> Order:
        with self.session_local() as sess:
            order = sess.query(Order).filter(Order.order_id == order_id).one_or_none()
            return order

    def add(self, **kwargs):
        with self.session_local() as sess:
            order = Order(**kwargs)
            sess.add(order)
            sess.commit()

    def update(self,
               order_id: int,
               order_number: int,
               price_usd: float,
               price_rub: float,
               delivery_date: datetime.date
        ):
        with self.session_local() as sess:
            order = self.get_by_id(order_id)
            order.order_number = order_number
            order.price_usd = price_usd
            order.price_rub = price_rub
            order.delivery_date = delivery_date
            sess.add(order)
            sess.commit()

    def delete(self, order_id: int):
        with self.session_local() as sess:
            order = self.get_by_id(order_id)
            sess.delete(order)
            sess.commit()
