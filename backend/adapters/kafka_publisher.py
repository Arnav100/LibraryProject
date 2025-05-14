from confluent_kafka import Producer
from backend.domain import events

class KafkaPublisher:
    def __init__(self, bootstrap_servers: str, topic: str = "my-topic"):
        self.producer: Producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            # 'client.id': 'library-service'
        })
        self.topic = topic
    
    def _publish(self, event: events.Event):
        self.producer.produce(
                self.topic,
                event.serialize(),
                callback=self._delivery_report
            )
        self.producer.flush()
    
    def _notify(self, event: events.Notification):
        self.producer.produce(
            "notifications",
            event.serialize(),
            callback=self._delivery_report
        )
        self.producer.flush()
    
    def publish(self, event: events.Event):
        try:
            if isinstance(event, events.Notification):
                self._notify(event)
            else:
                self._publish(event)    
        except Exception as e:
            print(f"Error publishing event {event}: {str(e)}")
            raise

    def _delivery_report(self, err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
