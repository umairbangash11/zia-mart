from aiokafka import AIOKafkaProducer

async def get_kafka_producer():
    return AIOKafkaProducer(bootstrap_servers='localhost:9092')
