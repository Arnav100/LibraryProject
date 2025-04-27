from confluent_kafka import Consumer, KafkaError
import json
from backend.domain import events
from backend.service_layer import messagebus

class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, bus: messagebus.MessageBus):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.messagebus = bus

    def subscribe(self, topics: list[str]):
        self.consumer.subscribe(topics)

    def start_consuming(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        continue

                event_data = json.loads(msg.value().decode('utf-8'))
                event_type = event_data['event_type']
                event_class = getattr(events, event_type)
                event = event_class(**event_data['payload'])
                
                # print(f"Received event: {event}")
                self.messagebus.handle(event)

        except KeyboardInterrupt:
            print("Consumer stopped by user")
        finally:
            self.consumer.close() 