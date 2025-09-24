#!/bin/bash

echo "=== Readloom Docker Debug Script ==="
echo "Checking if Readloom is running..."

# Check if the process is running
if pgrep -f "python.*Readloom.py" > /dev/null; then
    echo "✓ Readloom process is running"
    ps aux | grep "python.*Readloom.py" | grep -v grep
else
    echo "✗ Readloom process is NOT running"
fi

# Check if the port is open
echo -e "\nChecking if port 7227 is open..."
if nc -z localhost 7227; then
    echo "✓ Port 7227 is open on localhost"
else
    echo "✗ Port 7227 is NOT open on localhost"
fi

# Check if the port is listening on all interfaces
echo -e "\nChecking network interfaces..."
netstat -tulpn | grep 7227 || echo "✗ No process listening on port 7227"

# Check if we can connect to the web server
echo -e "\nTrying to connect to web server..."
curl -v http://localhost:7227/ 2>&1 | grep -E 'Connected|HTTP/'

echo -e "\nNetwork interface configuration:"
ip addr

echo -e "\nRouting table:"
ip route

echo -e "\n=== End of Debug Info ==="
