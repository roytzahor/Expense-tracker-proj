#!/bin/bash

# Set the namespace for Argo CD installation
ARGOCD_NAMESPACE="argocd"

echo "Creating namespace..."
kubectl create namespace $ARGOCD_NAMESPACE

# Adding Argo CD Helm repository
echo "Adding Argo CD Helm repository..."
helm repo add argo https://argoproj.github.io/argo-helm

# Update Helm repositories
echo "Updating Helm repositories..."
helm repo update

# List Helm repositories
echo "List of Helm repositories:"
helm repo ls

# Search for the Argo CD Helm chart
echo "Searching for Argo CD Helm chart..."
helm search repo argocd

# Search for the Argo CD Helm chart with detailed output
echo "Searching for Argo CD Helm chart with detailed output..."
helm search repo argo/argo-cd -l

# Show values for the Argo CD Helm chart
echo "Showing values for the Argo CD Helm chart..."
helm show values argo/argo-cd --version 3.35.4

# Create directory for values file
mkdir -p argocd/values

# Save values for the Argo CD Helm chart to a file
echo "Saving values for the Argo CD Helm chart to a file..."
helm show values argo/argo-cd --version 3.35.4 > argocd/values/argocd.yaml

# Install Argo CD using Helm
echo "Installing Argo CD using Helm..."
helm install argocd -n argocd --create-namespace argo/argo-cd --version 3.35.4 -f argocd/values/argocd.yaml

# Upgrade and install Argo CD using Helm
echo "Upgrading and installing Argo CD using Helm..."
helm upgrade --install argocd -n argocd --create-namespace argo/argo-cd --version 5.51.4 --wait

# Applying Argo CD manifests directly
echo "Applying Argo CD manifests directly..."
kubectl apply -n $ARGOCD_NAMESPACE -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "Argo CD is being installed, waiting to get ready..."
# Optionally, wait for the Argo CD server to be ready
kubectl rollout status deployment/argocd-server -n $ARGOCD_NAMESPACE

# Setting up port forwarding
echo "Setting up port forwarding..."
kubectl port-forward svc/argocd-server -n $ARGOCD_NAMESPACE 4001:443 >/dev/null 2>&1 &

echo "To navigate to Argo CD UI, go to: http://localhost:4001"
echo "Retrieving Argo CD admin password..."
ARGOCD_PASSWORD=$(kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 --decode)
echo "Argo CD password is: $ARGOCD_PASSWORD"

