from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import database
import service


class Settings:
    db = database.Settings()


class DB:
    engine = create_engine(Settings.db.DB_URL)
    database.Base.metadata.create_all(engine)

    session_local = sessionmaker(engine)

    orders_repo = database.repository.OrdersRepo(session_local=session_local)


class Application:
    app = service.GoogleSheetParser(
        "1sS7vJnIY6405dfDDjhVzOv19IRfEk5UIrrkW_4_xOv4",
        "A2:E",
        orders_repo=DB.orders_repo
    )


if __name__ == "__main__":
    Application.app.fill_database()
