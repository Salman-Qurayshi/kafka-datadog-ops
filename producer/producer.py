#!/usr/bin/env python3

import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProducer:
    def __init__(self, bootstrap_servers=['kafka:29092']):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )

    def generate_sample_data(self):
        """Generate sample IoT sensor data"""
        return {
            'sensor_id': f'sensor_{random.randint(1, 100)}',
            'temperature': round(random.uniform(15.0, 35.0), 2),
            'humidity': round(random.uniform(30.0, 90.0), 2),
            'timestamp': datetime.now().isoformat(),
            'location': random.choice(['warehouse_a', 'warehouse_b', 'warehouse_c'])
        }

    def send_messages(self, topic='sensor-data', num_messages=1000000): # Increased num_messages for continuous flow
        """Send messages to Kafka topic"""
        try:
            message_count = 0
            while True: # Keep sending messages indefinitely
                data = self.generate_sample_data()
                key = data['sensor_id']

                # Send message
                future = self.producer.send(topic, key=key, value=data)

                # Wait for message to be sent
                record_metadata = future.get(timeout=10)

                logger.info(f"Message {message_count+1} sent to {record_metadata.topic} "
                            f"partition {record_metadata.partition} "
                            f"offset {record_metadata.offset} | Data: {data['sensor_id']}, Temp: {data['temperature']}")

                message_count += 1
                time.sleep(1)  # Send one message per second

        except KeyboardInterrupt:
            logger.info("Producer interrupted by user.")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
        finally:
            self.producer.close()
            logger.info("Producer closed.")


if __name__ == "__main__":
    producer = DataProducer()
    producer.send_messages()