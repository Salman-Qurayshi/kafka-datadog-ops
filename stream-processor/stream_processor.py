#!/usr/bin/env python3

import json
import time
import logging
from collections import deque
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SENSOR_DATA_TOPIC = 'sensor-data'
ALERTS_TOPIC = 'alerts'
BOOTSTRAP_SERVERS = ['kafka:29092']
MOVING_AVERAGE_WINDOW_SIZE = 5 # Number of data points for moving average
TEMPERATURE_THRESHOLD = 30.0   # Temperature above which an alert is generated
ANOMALY_STD_DEV_MULTIPLIER = 2.0 # Multiplier for standard deviation to detect anomaly

class StreamProcessor:
    def __init__(self):
        self.consumer = KafkaConsumer(
            SENSOR_DATA_TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id='stream-processor-group',
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        # Store recent temperatures for each sensor to calculate moving average and std dev
        self.sensor_data_history = {} # {sensor_id: deque of temperatures}

    def calculate_moving_average_and_std_dev(self, sensor_id, current_temp):
        if sensor_id not in self.sensor_data_history:
            self.sensor_data_history[sensor_id] = deque(maxlen=MOVING_AVERAGE_WINDOW_SIZE)

        self.sensor_data_history[sensor_id].append(current_temp)

        # Ensure we have enough data points for calculation
        if len(self.sensor_data_history[sensor_id]) < MOVING_AVERAGE_WINDOW_SIZE:
            return None, None, None # Not enough data yet

        temperatures = list(self.sensor_data_history[sensor_id])
        avg = sum(temperatures) / len(temperatures)

        # Calculate standard deviation
        variance = sum([(x - avg) ** 2 for x in temperatures]) / len(temperatures)
        std_dev = variance ** 0.5

        return avg, std_dev, temperatures

    def generate_alert(self, sensor_id, current_temp, avg_temp, std_dev, anomaly_type):
        alert_message = {
            'alert_id': f"alert_{int(time.time() * 1000)}_{random.randint(100,999)}",
            'sensor_id': sensor_id,
            'current_temperature': current_temp,
            'average_temperature_last_N_readings': round(avg_temp, 2),
            'standard_deviation_last_N_readings': round(std_dev, 2),
            'anomaly_type': anomaly_type,
            'message': f"Anomaly detected for {sensor_id}: Current temp {current_temp}°C. Moving avg: {round(avg_temp, 2)}°C, Std Dev: {round(std_dev, 2)}°C. {anomaly_type}.",
            'timestamp': datetime.now().isoformat(),
            'severity': 'critical' if 'Critical' in anomaly_type else 'warning'
        }
        logger.warning(f"ALERT PRODUCED: {alert_message['message']}")
        self.producer.send(ALERTS_TOPIC, key=sensor_id, value=alert_message)


    def process_message(self, message):
        """Process individual message from sensor-data topic"""
        try:
            data = message.value
            sensor_id = data.get('sensor_id')
            current_temp = data.get('temperature')
            timestamp = data.get('timestamp')

            if sensor_id and current_temp is not None:
                logger.info(f"Stream Processor received data for {sensor_id}: Temp={current_temp}°C at {timestamp}")

                avg_temp, std_dev, history = self.calculate_moving_average_and_std_dev(sensor_id, current_temp)

                if avg_temp is not None: # Enough data to calculate
                    # Rule 1: Simple threshold alert
                    if current_temp > TEMPERATURE_THRESHOLD:
                        self.generate_alert(sensor_id, current_temp, avg_temp, std_dev, "High Temperature Threshold Exceeded")

                    # Rule 2: Anomaly detection based on standard deviation
                    # If current temp deviates significantly from moving average
                    if abs(current_temp - avg_temp) > (std_dev * ANOMALY_STD_DEV_MULTIPLIER):
                        anomaly_type = "Critical Temperature Anomaly (Statistical Deviation)"
                        self.generate_alert(sensor_id, current_temp, avg_temp, std_dev, anomaly_type)

                    # Rule 3: Check for sudden drops
                    if len(history) == MOVING_AVERAGE_WINDOW_SIZE and current_temp < min(history[:-1]) and current_temp < (avg_temp - std_dev):
                         self.generate_alert(sensor_id, current_temp, avg_temp, std_dev, "Sudden Temperature Drop Anomaly")

            else:
                logger.warning(f"Received malformed data: {data}")

        except Exception as e:
            logger.error(f"Error processing message in stream processor: {e}")

    def consume_messages(self):
        """Consume messages from Kafka topics"""
        logger.info("Starting Stream Processor...")
        try:
            for message in self.consumer:
                self.process_message(message)

        except KeyboardInterrupt:
            logger.info("Stream Processor interrupted by user.")
        except KafkaError as e:
            logger.error(f"Kafka error in stream processor: {e}")
        finally:
            self.consumer.close()
            self.producer.close()
            logger.info("Stream Processor closed.")

if __name__ == "__main__":
    processor = StreamProcessor()
    processor.consume_messages()