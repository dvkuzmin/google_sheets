import os


user = os.getenv('DB_USER', 'test_user')
password = os.getenv('DB_PASSWORD', 'qwerty')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
database = os.getenv('DB_DATABASE', 'test_db')


class Settings:
    DB_URL: str = f"postgresql+psycopg2://{user}:" \
          f"{password}@{host}:{port}/{database}"
