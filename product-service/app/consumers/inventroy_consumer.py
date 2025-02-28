# from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
# import json
# from app.models.product_model import Product, ProductUpdate
# from app.crud.product_crud import validate_product_by_id
# from app.deps import get_session, get_kafka_producer
# from app.hello_ai import chat_completion
# from app.crud.inventory_crud import add_new_inventory_item,delete_inventory_item, update_inventory_item
# from app.models.inventory_model import InventoryItem

# async def consume_inventory_messages(topic, bootstrap_servers):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=bootstrap_servers,
#         group_id="inventory-action-group",
#         # auto_offset_reset="earliest",
#     )

#     # Start the consumer.
#     await consumer.start()
#     try:
#         # Continuously listen for messages.
#         async for message in consumer:
#             print("\n\n RAW INVENTORY MESSAGE\n\n ")
#             print(f"Received message on topic {message.topic}")
#             print(f"Message Value {message.value}")

#             # Parse the message
#             inventory_data = json.loads(message.value.decode())
#             product_id = inventory_data["product_id"]
#             action = inventory_data.get("action", "add")  # Default to "add" if action is missing

#             print("PRODUCT ID:", product_id)
#             print("ACTION:", action)

#             with next(get_session()) as session:
#                 # Check if the product ID is valid.
#                 product = validate_product_by_id(
#                     product_id=product_id, session=session)
#                 print("PRODUCT VALIDATION CHECK", product)

#                 if product is None:
#                     # Notify admin if the product is not found.
#                     email_body = chat_completion(
#                         f"Admin has Sent Incorrect Product. Write Email to Admin {product_id}")
#                     print("EMAIL SENT TO ADMIN:", email_body)
#                 else:
#                     # Process based on the action type
#                     if action == "add":
#                         # Add the product to the inventory.
#                         inventory_item = InventoryItem(**inventory_data)
#                         add_new_inventory_item(inventory_item_data=inventory_item, session=session)
#                         print("Added product to inventory:", inventory_item)
                    
#                     elif action == "update":
#                         # Update the product details in the inventory.
#                         update_inventory_item(product_id=product_id, inventory_item_data=inventory_data, session=session)
#                         print("Updated product in inventory:", inventory_data)

#                     elif action == "delete":
#                         # Delete the product from the inventory.
#                         delete_inventory_item(product_id=product_id, session=session)
#                         print("Deleted product from inventory:", product_id)

#                     # Send a response message back to confirm the action.
#                     producer = AIOKafkaProducer(
#                         bootstrap_servers='broker:19092')
#                     await producer.start()
#                     try:
#                         await producer.send_and_wait(
#                             "inventory-action-response",
#                             json.dumps({
#                                 "product_id": product_id,
#                                 "action": action,
#                                 "status": "success"
#                             }).encode()
#                         )
#                     finally:
#                         await producer.stop()

#     finally:
#         # Ensure to close the consumer when done.
#         await consumer.stop()
