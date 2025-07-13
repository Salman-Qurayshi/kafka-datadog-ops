# kafka-datadog-ops/producer/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install required packages
RUN pip install kafka-python

# Copy application code
COPY producer.py .

# Run the producer
CMD ["python", "producer.py"]