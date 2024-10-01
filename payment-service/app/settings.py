from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
KAFKA_TRANSACTION_TOPIC = config("KAFKA_TRANSACTION_TOPIC", cast=str)




BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_TRANSACTION= config("KAFKA_CONSUMER_GROUP_ID_FOR_TRANSACTION", cast=str)



TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)
