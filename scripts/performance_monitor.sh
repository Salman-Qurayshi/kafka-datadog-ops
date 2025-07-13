#!/bin/bash
# kafka-datadog-ops/scripts/performance_monitor.sh

echo "--- System Performance Monitor ---"
echo "Monitoring CPU and Memory usage every 2 seconds. Press Ctrl+C to stop."

while true; do
    echo "---------------------------------"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

    # CPU Usage (using mpstat or fallback to top/grep)
    if command -v mpstat &> /dev/null; then
        mpstat 1 1 | grep "Average" | awk '{print "CPU Idle: " $NF "%"}'
    else
        top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/CPU Idle: \1%/"
    fi

    # Memory Usage (using free)
    free -h | grep "Mem:" | awk '{print "Total Memory: " $2 ", Used Memory: " $3 ", Free Memory: " $4}'

    # Disk Usage (for the current directory's filesystem)
    df -h . | grep -v Filesystem | awk '{print "Disk Used: " $5 " of " $2 " on " $1}'

    # Container Status Overview (using docker ps)
    echo -e "\n--- Docker Container Status ---"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    sleep 2
done