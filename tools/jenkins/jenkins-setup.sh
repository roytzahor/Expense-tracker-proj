#!/bin/bash

# Set the namespace for Jenkins installation
JENKINS_NAMESPACE="jenkins"

echo "Creating namespace..."
kubectl create namespace $JENKINS_NAMESPACE

# Adding Jenkins Helm repository
echo "Adding Jenkins Helm repository..."
helm repo add jenkins https://charts.jenkins.io

# Update Helm repositories
echo "Updating Helm repositories..."
helm repo update

# List Helm repositories
echo "List of Helm repositories:"
helm repo ls

# Search for the Jenkins Helm chart
echo "Searching for Jenkins Helm chart..."
helm search repo jenkins

# Show values for the Jenkins Helm chart
echo "Showing values for the Jenkins Helm chart..."
helm show values jenkins/jenkins

# Create directory for values file
mkdir -p jenkins/values

# Save default values for the Jenkins Helm chart to a file
echo "Saving default values for the Jenkins Helm chart to a file..."
helm show values jenkins/jenkins > jenkins/values/jenkins.yaml

# Edit jenkins/values/jenkins.yaml as needed before proceeding

# Install Jenkins using Helm
echo "Installing Jenkins using Helm..."
helm install jenkins -n $JENKINS_NAMESPACE --create-namespace jenkins/jenkins -f jenkins/values/jenkins.yaml

echo "Jenkins is being installed, waiting to get ready..."
# Optionally, wait for the Jenkins deployment to be ready
kubectl rollout status deployment/jenkins -n $JENKINS_NAMESPACE

# Get the Jenkins administrator password
echo "Retrieving Jenkins admin password..."
JENKINS_PASSWORD=$(kubectl get secret -n $JENKINS_NAMESPACE jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode)
echo "Jenkins admin password is: $JENKINS_PASSWORD"

# Setting up port forwarding to access Jenkins
echo "Setting up port forwarding to access Jenkins UI..."
kubectl port-forward svc/jenkins -n $JENKINS_NAMESPACE 8081:8080 >/dev/null 2>&1 &

echo "Jenkins setup is complete. You can access the Jenkins UI at http://localhost:8080"
echo "Login with the username 'admin' and the admin password displayed above."
