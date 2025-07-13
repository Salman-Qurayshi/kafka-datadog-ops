#!/usr/bin/env python3

import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataConsumer:
    def __init__(self, topics=['sensor-data'], bootstrap_servers=['kafka:29092']):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='sensor-consumer-group',
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )

    def process_message(self, message):
        """Process individual message"""
        try:
            data = message.value
            key = message.key

            # Simple processing - log temperature alerts
            if data.get('temperature', 0) > 30:
                logger.warning(f"HIGH TEMPERATURE ALERT (simple consumer): {data}")
            else:
                logger.info(f"Normal reading from {key} (simple consumer): "
                            f"Temp={data.get('temperature')}°C, "
                            f"Humidity={data.get('humidity')}%")

        except Exception as e:
            logger.error(f"Error processing message in simple consumer: {e}")

    def consume_messages(self):
        """Consume messages from Kafka topics"""
        logger.info("Starting simple consumer...")
        try:
            for message in self.consumer:
                self.process_message(message)

        except KeyboardInterrupt:
            logger.info("Simple consumer interrupted by user")
        except KafkaError as e:
            logger.error(f"Kafka error in simple consumer: {e}")
        finally:
            self.consumer.close()
            logger.info("Simple consumer closed.")

if __name__ == "__main__":
    consumer = DataConsumer()
    consumer.consume_messages()