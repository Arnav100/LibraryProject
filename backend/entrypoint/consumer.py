from backend.adapters.kafka_consumer import KafkaConsumer
from backend import bootstrap
import os
def main():
    # Initialize Kafka consumer
    bus = bootstrap.bootstrap()

    kafka_bootstrap_servers: str = os.getenv('KAFKA_BOOTSTRAP_SERVERS') or 'localhost:9092'
    consumer = KafkaConsumer(
        bootstrap_servers=kafka_bootstrap_servers,
        group_id='library-service-group',
        bus=bus
    )

    topics = ["my-topic"]
    consumer.subscribe(topics)

    print("Starting Kafka consumer...")
    consumer.start_consuming()

if __name__ == "__main__":
    main() 