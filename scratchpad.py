from confluent_kafka import Producer

from backend.domain.events import BookReturned, BookCheckedOut, BookPlacedOnHold, BookAdded, BookRemoved, Notification
from backend.adapters.kafka_publisher import KafkaPublisher


publisher = KafkaPublisher('localhost:9092',  topic='notifications')

publisher.publish(Notification(user_id=1, type='hold_updated', message='Hello, world!'))

