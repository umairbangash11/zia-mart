from aiokafka import AIOKafkaProducer
import json
from app.models.order_model import Order

async def produce_order_event(order: Order):
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        # Convert order object to JSON
        order_json = json.dumps(order.dict()).encode('utf-8')

        # Send the order event to the Kafka topic
        await producer.send('order-events', order_json)
        print(f"Order event produced: {order_json}")
    finally:
        await producer.stop()