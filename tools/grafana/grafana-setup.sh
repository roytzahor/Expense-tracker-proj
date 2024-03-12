#!/bin/bash

# Create a monitoring namespace if it doesn't exist

# Add the Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts

# Update your Helm repository
helm repo update

# Install Grafana using Helm into the monitoring namespace
helm upgrade --install grafana grafana/grafana \
    --namespace monitoring

# Get the Grafana URL to visit by running these commands in the same shell
export GRAFANA_POD_NAME=$(kubectl get pods --namespace monitoring -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")
echo "Visit http://localhost:3000 to access Grafana"

kubectl port-forward svc/grafana -n monitoring 3000:80 > /dev/null 2>&1 &

echo "finished"
