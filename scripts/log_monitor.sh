#!/bin/bash
CONTAINER_NAME=$1

if [ -z "$CONTAINER_NAME" ]; then
    echo "Usage: $0 <container_name>"
    echo "Example: $0 kafka-producer"
    echo "Available containers:"
    docker ps --format "{{.Names}}"
    exit 1
fi

echo "Tailing logs for container: $CONTAINER_NAME. Press Ctrl+C to stop."
docker logs -f "$CONTAINER_NAME"