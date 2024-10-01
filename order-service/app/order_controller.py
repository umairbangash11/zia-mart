from fastapi import APIRouter, Depends
import asyncio
import json
from .producer import get_kafka_producer

app = APIRouter()

@app.post("/create_order/")
async def create_order(order_id: int, product_id: int):
    producer = await get_kafka_producer()
    await producer.start()
    
    order_event = {
        "order_id": order_id,
        "product_id": product_id
    }
    try:
        await producer.send_and_wait("order-events", json.dumps(order_event).encode())
    finally:
        await producer.stop()

    return {"status": "Order Created", "order_id": order_id}
