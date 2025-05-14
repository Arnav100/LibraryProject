from backend.adapters.kafka_consumer import KafkaConsumer
from backend import bootstrap
import os
import asyncio

async def main():
    # Initialize Kafka consumer
    bus = bootstrap.bootstrap()

    kafka_bootstrap_servers: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS') or 'localhost:9092'
    consumer = KafkaConsumer(
        bootstrap_servers=kafka_bootstrap_servers,
        group_id='library-service-group',
    )

    topics = ["my-topic"]
    consumer.subscribe(topics)

    print("Starting Kafka consumer...")
    try:
        async for event in consumer.start_consuming():
            bus.handle(event)
    except KeyboardInterrupt:
        print("\nShutting down consumer...")
    finally:
        consumer.stop()

if __name__ == "__main__":
    asyncio.run(main()) 