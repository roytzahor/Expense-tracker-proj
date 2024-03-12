#!/bin/bash

# Set the namespace variable
NAMESPACE=monitoring

# Check if the monitoring namespace exists, and create it if not
kubectl get ns $NAMESPACE || kubectl create ns $NAMESPACE

# Add the Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Update your local Helm chart repository cache
helm repo update

# Install Prometheus via Helm
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --values ./tools/prometheus/values.yaml

helm upgrade prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --values ./tools/prometheus/values.yaml


# Get the Prometheus service info
kubectl get svc -n monitoring prometheus-server

kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring > /dev/null 2>&1 &  

kubectl port-forward svc/prometheus-kube-prometheus-alertmanager 9093:9093 -n monitoring > /dev/null 2>&1 &

