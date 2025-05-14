from confluent_kafka import Consumer, KafkaError
import json
from backend.domain import events
from typing import AsyncGenerator
import asyncio

class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.running = True

    def subscribe(self, topics: list[str]):
        self.consumer.subscribe(topics)

    async def start_consuming(self) -> AsyncGenerator[events.Event, None]:
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        continue

                try:
                    event_data = json.loads(msg.value().decode('utf-8'))
                    event_type = event_data['event_type']
                    event_class = getattr(events, event_type)
                    event = event_class(**event_data['payload'])
                    yield event
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue

        except Exception as e:
            print(f"Consumer error: {e}")
        finally:
            self.consumer.close()

    def stop(self):
        self.running = False 