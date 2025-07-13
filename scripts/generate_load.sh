#!/bin/bash
# kafka-datadog-ops/scripts/generate_load.sh

echo "Starting to generate load on Kafka UI (port 8080)... Press Ctrl+C to stop."
echo "This script repeatedly hits the Kafka UI endpoint to simulate web traffic."
echo "The Kafka Producer is generating the main data load."

while true; do
    curl -s http://localhost:8080/
    sleep 1
done