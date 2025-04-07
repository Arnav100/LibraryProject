from confluent_kafka import Producer, Consumer, KafkaError, Message
import json
from typing import Callable, Dict, Type
from backend.domain import events
import logging
from functools import wraps


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

class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.event_handlers: Dict[Type[events.Event], Callable] = {}

    def subscribe(self, topics: list[str]):
        self.consumer.subscribe(topics)

    def register_handler(self, event_type: Type[events.Event], handler: Callable):
        self.event_handlers[event_type] = handler

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
                
                print(f"Received event: {event}")
                if event_class in self.event_handlers:
                    self.event_handlers[event_class](event)
     

        except KeyboardInterrupt:
            print("Consumer stopped by user")
        finally:
            self.consumer.close() 