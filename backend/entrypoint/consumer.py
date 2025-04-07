import logging
from backend.adapters.kafka import KafkaConsumer
from backend.service_layer import event_handlers, unit_of_work
from backend.domain import events
from backend import bootstrap
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        bootstrap_servers='localhost:9092',
        group_id='library-service-group'
    )

    # Initialize Unit of Work
    bus = bootstrap.bootstrap()
    uow = bus.uow

    # Register event handlers
    for event_type, handler in event_handlers.EVENT_HANDLERS.items():
        consumer.register_handler(event_type, lambda e, h=handler: h(e, uow))

    # Subscribe to all event topics
    # topics = [event.__name__.lower() for event in events.Event.__subclasses__()]
    topics = ["my-topic"]
    consumer.subscribe(topics)

    print("Starting Kafka consumer...")
    consumer.start_consuming()

if __name__ == "__main__":
    main() 