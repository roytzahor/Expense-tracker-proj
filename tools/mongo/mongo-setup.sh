#!/bin/bash

# Set the release name for your MongoDB deployment
RELEASE_NAME="mongodb"

# Add the Bitnami Helm repository
echo "Adding the Bitnami repository to Helm..."
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update your local Helm chart repository cache
echo "Updating Helm repository..."
helm repo update

# Install MongoDB from the Bitnami chart with a specific version
echo "Installing MongoDB version  with Helm..."
helm install $RELEASE_NAME bitnami/mongodb

# After installation, you can check the status of your MongoDB release
echo "Checking the release status..."
helm status $RELEASE_NAME

# this is to add mongodb to argocd ui 
kubectl apply -f mongo.yaml -n argocd

# Forward the MongoDB service port to localhost
echo "Forwarding MongoDB service port to localhost..."
kubectl port-forward svc/mongo 27017:27017 

# Output the commands to connect to your MongoDB database
echo "To connect to your MongoDB database, follow the instructions provided in the Helm chart notes after installation."
