# kafka-datadog-ops/consumer/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install required packages
RUN pip install kafka-python

# Copy application code
COPY consumer.py .

# Run the consumer
CMD ["python", "consumer.py"]