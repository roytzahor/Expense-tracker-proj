#!/bin/sh
# Start the Flask app in the background
python3 app.py &

# Wait a bit for the Flask server to start
sleep 5

# Run unittest
python3 -m unittest test_app.py