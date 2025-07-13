# kafka-datadog-ops/stream-processor/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install required packages
RUN pip install kafka-python numpy

# Copy all application code (both stream_processor.py and alert_consumer.py)
COPY stream_processor.py .
COPY alert_consumer.py .

# Default command for the stream-processor service
# The alert-consumer service will override this using 'command' in docker-compose.yml
CMD ["python", "stream_processor.py"]