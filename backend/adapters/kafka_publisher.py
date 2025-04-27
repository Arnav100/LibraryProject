from confluent_kafka import Producer
from backend.domain import events

class KafkaPublisher:
    def __init__(self, bootstrap_servers: str):
        self.producer: Producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            # 'client.id': 'library-service'
        })

    def publish(self, event: events.Event):
        try:
            topic = "my-topic"
            self.producer.produce(
                topic,
                event.serialize(),
                callback=self._delivery_report
            )
            self.producer.flush()
        except Exception as e:
            print(f"Error publishing event {event}: {str(e)}")
            raise

    def _delivery_report(self, err, msg):
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
