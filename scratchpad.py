from confluent_kafka import Producer

from backend.domain.events import BookReturned, BookCheckedOut, BookPlacedOnHold, BookAdded, BookRemoved
from backend.adapters.kafka import KafkaPublisher

publisher = KafkaPublisher('localhost:9092')

publisher.publish(BookReturned(1, 1))
