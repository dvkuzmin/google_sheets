from .tables import Order
from dataclasses import dataclass
from sqlalchemy.orm.session import sessionmaker


@dataclass
class OrdersRepo:
    session_local: sessionmaker

    def get_all(self):
        with self.session_local() as sess:
            return sess.query(Order).all()
