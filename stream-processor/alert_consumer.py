#!/usr/bin/env python3

import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALERTS_TOPIC = 'alerts'
BOOTSTRAP_SERVERS = ['kafka:29092']

class AlertConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            ALERTS_TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='alert-consumer-group',
            auto_offset_reset='latest', # Start from latest alerts
            enable_auto_commit=True
        )

    def process_alert(self, alert_message):
        """Process individual alert message"""
        try:
            alert_id = alert_message.get('alert_id')
            sensor_id = alert_message.get('sensor_id')
            anomaly_type = alert_message.get('anomaly_type')
            severity = alert_message.get('severity')
            message = alert_message.get('message')
            timestamp = alert_message.get('timestamp')

            if severity == 'critical':
                logger.critical(f"*** CRITICAL ALERT (Alert Consumer) *** [{alert_id}] {sensor_id}: {anomaly_type} - {message} at {timestamp}")
            else:
                logger.warning(f"--- ALERT (Alert Consumer) --- [{alert_id}] {sensor_id}: {anomaly_type} - {message} at {timestamp}")

        except Exception as e:
            logger.error(f"Error processing alert: {e}")

    def consume_alerts(self):
        """Consume alert messages from Kafka topic"""
        logger.info("Starting Alert Consumer...")
        try:
            for message in self.consumer:
                self.process_alert(message.value)

        except KeyboardInterrupt:
            logger.info("Alert Consumer interrupted by user.")
        except KafkaError as e:
            logger.error(f"Kafka error in alert consumer: {e}")
        finally:
            self.consumer.close()
            logger.info("Alert Consumer closed.")

if __name__ == "__main__":
    consumer = AlertConsumer()
    consumer.consume_alerts()