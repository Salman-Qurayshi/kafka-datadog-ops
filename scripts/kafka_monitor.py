#!/usr/bin/env python3

from kafka import KafkaClient, KafkaConsumer
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOOTSTRAP_SERVERS = ['localhost:9092'] # Connects to Kafka via exposed host port

def get_kafka_client():
    try:
        client = KafkaClient(bootstrap_servers=BOOTSTRAP_SERVERS)
        client.check_version()
        logger.info("Successfully connected to Kafka cluster.")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Kafka cluster: {e}")
        return None

def list_topics(client):
    if not client:
        return
    logger.info("\n--- Kafka Topics ---")
    try:
        topics = client.topics
        if topics:
            for topic_name, topic_metadata in topics.items():
                logger.info(f"Topic: {topic_name.decode('utf-8')}")
                # You can add more details from topic_metadata if needed
        else:
            logger.info("No topics found.")
    except Exception as e:
        logger.error(f"Error listing topics: {e}")

def list_consumer_groups(client):
    if not client:
        return
    logger.info("\n--- Kafka Consumer Groups ---")
    try:
        # Need a consumer for listing groups reliably
        consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS, client_id='kafka-monitor-client')
        groups = consumer.consumer_groups()
        if groups:
            for group_id, metadata in groups:
                group_id_str = group_id.decode('utf-8')
                logger.info(f"Group ID: {group_id_str}")
                # You can add more details from metadata if needed, e.g., partitions assigned
                try:
                    offsets = consumer.end_offsets(consumer.partitions_for_topic("sensor-data")) # Example for sensor-data topic
                    logger.info(f"  End offsets for sensor-data: {offsets}")
                except Exception as e:
                    logger.warning(f"  Could not get end offsets for sensor-data for group {group_id_str}: {e}")

        else:
            logger.info("No consumer groups found.")
        consumer.close()
    except Exception as e:
        logger.error(f"Error listing consumer groups: {e}")


if __name__ == "__main__":
    logger.info("Starting Kafka Monitor...")
    kafka_client = get_kafka_client()
    if kafka_client:
        list_topics(kafka_client)
        list_consumer_groups(kafka_client)
        kafka_client.close()
    logger.info("Kafka Monitor finished.")