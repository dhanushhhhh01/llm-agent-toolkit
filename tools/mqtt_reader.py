"""
MQTT Reader Tool - Enables LLM agents to read from MQTT topics.
Used for IIoT/industrial applications where agents need real-time sensor data.
"""
import json
import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import logging

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


@dataclass
class MQTTMessage:
      topic: str
      payload: str
      qos: int
      timestamp: float = field(default_factory=time.time)

    def as_dict(self) -> Dict:
              return {
                            "topic": self.topic,
                            "payload": self.payload,
                            "qos": self.qos,
                            "timestamp": self.timestamp
              }


class MQTTReaderTool:
      """
          MQTT subscriber tool for LLM agents.

                  Allows agents to:
                      - Subscribe to topics and read latest messages
                          - Get message history for a topic
                              - Query specific sensor values
                                  """

    def __init__(
              self,
              broker_url: str = "localhost",
              broker_port: int = 1883,
              username: Optional[str] = None,
              password: Optional[str] = None,
              buffer_size: int = 100
    ):
              self.broker_url = broker_url
              self.broker_port = broker_port
              self.buffer_size = buffer_size
              self._messages: Dict[str, List[MQTTMessage]] = {}
              self._connected = False
              self._lock = threading.Lock()

        # Setup MQTT client
              self.client = mqtt.Client(client_id=f"llm-agent-{int(time.time())}")
              if username:
                            self.client.username_pw_set(username, password)

              self.client.on_connect = self._on_connect
              self.client.on_message = self._on_message
              self.client.on_disconnect = self._on_disconnect

    def connect(self) -> bool:
              """Connect to MQTT broker."""
              try:
                            self.client.connect(self.broker_url, self.broker_port, keepalive=60)
                            self.client.loop_start()
                            time.sleep(1)  # Wait for connection
            return self._connected
except Exception as e:
            logger.error(f"MQTT connect failed: {e}")
            return False

    def disconnect(self):
              """Disconnect from broker."""
              self.client.loop_stop()
              self.client.disconnect()
              self._connected = False

    def subscribe(self, topic: str, qos: int = 0):
              """Subscribe to an MQTT topic."""
              with self._lock:
                            if topic not in self._messages:
                                              self._messages[topic] = []
                                      self.client.subscribe(topic, qos)
                        logger.info(f"Subscribed to: {topic}")

    def get_latest(self, topic: str) -> Optional[Dict]:
              """
                      Get the latest message from a topic.
                              This is the tool function exposed to LLM agents.
                                      """
        with self._lock:
                      messages = self._messages.get(topic, [])
                      if not messages:
                                        return {"error": f"No messages received on topic: {topic}"}
                                    latest = messages[-1]
            return latest.as_dict()

    def get_history(self, topic: str, count: int = 10) -> List[Dict]:
              """Get recent message history from a topic."""
        with self._lock:
                      messages = self._messages.get(topic, [])
            return [m.as_dict() for m in messages[-count:]]

    def get_sensor_value(self, topic: str, field: str) -> Optional[float]:
              """
                      Extract a specific field from the latest JSON message.
                              Useful for agents querying specific sensor readings.
                                      """
        latest = self.get_latest(topic)
        if not latest or "error" in latest:
                      return None
        try:
                      payload = json.loads(latest["payload"])
            return payload.get(field)
except (json.JSONDecodeError, TypeError):
            return None

    def _on_connect(self, client, userdata, flags, rc):
              if rc == 0:
                            self._connected = True
                            logger.info(f"Connected to MQTT broker: {self.broker_url}:{self.broker_port}")
else:
            logger.error(f"MQTT connection failed with code: {rc}")

    def _on_message(self, client, userdata, message):
              topic = message.topic
        try:
                      payload = message.payload.decode("utf-8")
except Exception:
            payload = str(message.payload)

        msg = MQTTMessage(
                      topic=topic,
                      payload=payload,
                      qos=message.qos
        )

        with self._lock:
                      if topic not in self._messages:
                                        self._messages[topic] = []
                                    self._messages[topic].append(msg)
            # Keep buffer size
            if len(self._messages[topic]) > self.buffer_size:
                              self._messages[topic] = self._messages[topic][-self.buffer_size:]

    def _on_disconnect(self, client, userdata, rc):
              self._connected = False
        logger.warning(f"Disconnected from MQTT broker (rc={rc})")

    # Tool schema for LLM agent registration
    @staticmethod
    def get_tool_schema() -> Dict:
              return {
                            "type": "object",
                            "properties": {
                                              "topic": {
                                                                    "type": "string",
                                                                    "description": "MQTT topic to read from (e.g., 'sensors/temperature/device001')"
                                              }
                            },
                            "required": ["topic"]
              }
