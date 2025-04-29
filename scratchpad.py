from confluent_kafka import Producer

from backend.domain.events import BookReturned, BookCheckedOut, BookPlacedOnHold, BookAdded, BookRemoved
from backend.adapters.kafka_publisher import KafkaPublisher

publisher = KafkaPublisher('localhost:9092')

publisher.publish(BookReturned(4, 2))

