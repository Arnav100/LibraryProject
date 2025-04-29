from typing import Dict
from fastapi import WebSocket
import redis
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.redis = redis.Redis(host='localhost', port=6380, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('notifications')
        self.running = True
        self._notification_task = None

    async def start(self):
        """Start the notification listener task"""
        self._notification_task = asyncio.create_task(self.listen_for_notifications())

    async def stop(self):
        """Stop the notification listener task"""
        self.running = False
        if self._notification_task:
            self._notification_task.cancel()
            try:
                await self._notification_task
            except asyncio.CancelledError:
                pass
        self.pubsub.unsubscribe()
        self.redis.close()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def listen_for_notifications(self):
        while self.running:
            message = self.pubsub.get_message()
            if message and message['type'] == 'message':
                try:
                    notification = json.loads(message['data'])
                    user_id = str(notification['user_id'])
                    await self.send_personal_message(json.dumps(notification), user_id)
                except Exception as e:
                    print(f"Error handling notification: {e}")
            await asyncio.sleep(0.1) 