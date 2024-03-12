#!/bin/sh
# Start the Flask app in the background
python3 app.py &

# Wait a bit for the Flask server to start
sleep 5

# Run pytest
pytest test_app.py

# Optionally, kill the Flask app before exiting
# kill $!
