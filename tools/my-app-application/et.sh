#!/bin/bash

kubectl apply -f ./tools/my-app-application/et-application.yaml -n argocd

kubectl port-forward svc/et-application-expense-tracker-app 5000:5000 -n default > /dev/null 2>&1 &

echo "finish script!"