# Zia-Mart E-commerce Platform

A modern, scalable e-commerce platform built using microservices architecture. This platform provides a robust foundation for online retail operations with separate services handling different aspects of the business.

## 🏗️ Architecture

The platform is built using a microservices architecture with the following components:

- **API Gateway** (Port: 8000)
- **Product Service** (Port: 8005)
- **Inventory Service** (Port: 8006)
- **Order Service** (Port: 8007)
- **User Service** (Port: 8008)
- **Notification Service** (Port: 8009)
- **Payment Service** (Port: 8010)

## 🛠️ Technology Stack

- **Message Broker**: Apache Kafka
- **Database**: PostgreSQL (Multiple instances for each service)
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **API Framework**: FastAPI (Python)
- **Database ORM**: SQLModel

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zia-mart
```

2. Start the services:
```bash
docker-compose up -d
```

3. Access the services:
- API Gateway: http://localhost:8000
- Kafka UI: http://localhost:8080

## 📦 Services Overview

### Product Service
Manages product catalog, categories, and product-related operations.

### Inventory Service
Handles stock management, inventory tracking, and stock updates.

### Order Service
Manages order processing, order status, and order history.

### User Service
Handles user management, authentication, and user profiles.

### Notification Service
Manages notifications, alerts, and communication with users.

### Payment Service
Handles payment processing and transaction management.

## 🔄 Service Communication

Services communicate asynchronously using Apache Kafka as the message broker. Each service maintains its own database for data persistence.

## 📊 Database Configuration

Each service has its own PostgreSQL database instance:
- Product DB: Port 5481
- Inventory DB: Port 5482
- Order DB: Port 5483
- User DB: Port 5484
- Notification DB: Port 5485
- Payment DB: Port 5486

## 🔐 Environment Variables

Key environment variables for each service:
- `DATABASE_URL`: PostgreSQL connection string
- `BOOTSTRAP_SERVER`: Kafka broker address
- `KAFKA_ORDER_TOPIC`: Kafka topic for orders
- `KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT`: Kafka consumer group ID

## 🛠️ Development

### Local Development
Each service can be developed independently. The services are mounted as volumes in Docker, allowing for live code updates.

### Building Services
```bash
docker-compose build <service-name>
```

### Viewing Logs
```bash
docker-compose logs -f <service-name>
```

## 📝 License

[Add your license information here]

## 👥 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support information here]

# 02_kafka_messaging

### AIOKafkaProducer

AIOKafkaProducer is a high-level, asynchronous message producer.

Example of AIOKafkaProducer usage:

```
from aiokafka import AIOKafkaProducer

# Kafka Producer as a dependency
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait("my_topic", b"Super message")
    finally:
        await producer.stop()
```

### AIOKafkaConsumer
AIOKafkaConsumer is a high-level, asynchronous message consumer. It interacts with the assigned Kafka Group Coordinator node to allow multiple consumers to load balance consumption of topics (requires kafka >= 0.9.0.0).

Example of AIOKafkaConsumer usage:

```
from aiokafka import AIOKafkaConsumer
import asyncio

async def consume_messages():
    consumer = AIOKafkaConsumer(
        'my_topic', 'my_other_topic',
        bootstrap_servers='localhost:9092',
        group_id="my-group")
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

asyncio.create_task(consume_messages())
```

https://github.com/aio-libs/aiokafka