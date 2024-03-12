#!/bin/bash

# Stop on error
set -e

# Navigate to the directory with your scripts
cd ./tools/

# Run Argo CD setup script
echo "Starting Argo CD setup..."
./argocd/argocd-setup.sh
echo "Argo CD setup complete."

# Run Jenkins setup script
echo "Starting Jenkins setup..."
./jenkins/jenkins-setup.sh
echo "Jenkins setup complete."

# Run MongoDB setup script
# echo "Starting MongoDB setup..."
# ./mongo/mongo-setup.sh
# echo "MongoDB setup complete."

# Run your application setup script
echo "Starting application setup..."
./my-app-application/et.sh
echo "Application setup complete."

# Run Prometheus setup script
echo "Starting Prometheus setup..."
./prometheus/prometheus-setup.sh
echo "Prometheus setup complete."

# Run Grafana setup script
echo "Starting Grafana setup..."
./grafana/grafana-setup.sh
echo "Grafana setup complete."

echo "All scripts have been executed successfully."
