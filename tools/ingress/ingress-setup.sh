#!/bin/bash

# Deploy NGINX Ingress Controller
echo "Adding NGINX Ingress Controller Helm repository..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

echo "Updating Helm repositories..."
helm repo update

echo "Installing NGINX Ingress Controller..."
helm install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace

# Wait a bit to ensure the Ingress Controller is deployed
echo "Waiting for NGINX Ingress Controller to be ready..."
sleep 60

# Apply the Ingress rules
echo "Applying Ingress rules..."
kubectl apply -f jenkins-rule.yaml -n jenkins
kubectl apply -f argocd-rule.yaml -n argocd
kubectl apply -f monitoring-rule.yaml -n monitoring 

echo "Ingress setup complete. Services are now accessible via localhost with specified paths."
