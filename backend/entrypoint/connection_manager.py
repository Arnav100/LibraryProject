from typing import Dict
from fastapi import WebSocket
import asyncio
import json
import os
from backend.adapters.kafka_consumer import KafkaConsumer
from backend.service_layer import messagebus
from backend.domain.events import Notification

class ConnectionManager:
    def __init__(self, bus: messagebus.MessageBus):
        self.active_connections: Dict[str, WebSocket] = {}
        self.kafka_consumer = None
        self.running = True
        self._notification_task = None
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.kafka_group_id = 'notification_group'

    async def start(self):
        """Start the Kafka consumer and notification listener task"""
        self.kafka_consumer = KafkaConsumer(
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id=self.kafka_group_id
        )
        self.kafka_consumer.subscribe(['notifications'])
        self._notification_task = asyncio.create_task(self.listen_for_notifications())

    async def stop(self):
        """Stop the notification listener task and Kafka consumer"""
        self.running = False
        if self._notification_task:
            self._notification_task.cancel()
            try:
                await self._notification_task
            except asyncio.CancelledError:
                pass
        if self.kafka_consumer:
            self.kafka_consumer.stop()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            print(f"Sending message to user {user_id}: {message}")
            await self.active_connections[user_id].send_json(message)

    async def listen_for_notifications(self):
        """Listen for notifications from Kafka and forward them to appropriate users"""
        try:
            async for event in self.kafka_consumer.start_consuming():
                if not self.running:
                    break
                try:
                    print(f"Received event: {event}")
                    if isinstance(event, Notification):
                        user_id = str(event.user_id)
                        await self.send_personal_message(event.serialize(), user_id)
                except Exception as e:
                    print(f"Error handling notification: {e}")
        except Exception as e:
            print(f"Error in notification listener: {e}")
