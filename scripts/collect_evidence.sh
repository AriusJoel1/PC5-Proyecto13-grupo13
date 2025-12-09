#!/usr/bin/env bash
set -euo pipefail

mkdir -p .evidence

echo "Namespaces:" > .evidence/k8s-namespaces.txt
kubectl get ns >> .evidence/k8s-namespaces.txt

echo "Deployments in platform:" > .evidence/platform-deploy.txt
kubectl get deployments -n platform >> .evidence/platform-deploy.txt

echo "Roles and RoleBindings:" > .evidence/roles.txt
kubectl get roles --all-namespaces >> .evidence/roles.txt
kubectl get rolebindings --all-namespaces >> .evidence/rolebindings.txt

echo "ServiceAccounts:" > .evidence/sas.txt
kubectl get sa --all-namespaces >> .evidence/sas.txt

echo "Pods status:" > .evidence/pods.txt
kubectl get pods --all-namespaces >> .evidence/pods.txt

echo "RBAC checks (kubectl auth can-i examples):" > .evidence/auth_checks.txt
kubectl auth can-i get configmaps --as system:serviceaccount:tenant-a:tenant-a-sa -n tenant-a >> .evidence/auth_checks.txt || true
kubectl auth can-i get secrets --as system:serviceaccount:tenant-a:tenant-a-sa -n tenant-a >> .evidence/auth_checks.txt || true
kubectl auth can-i get configmaps --as system:serviceaccount:tenant-a:tenant-a-sa -n tenant-b >> .evidence/auth_checks.txt || true

echo "Done. Evidence in .evidence/"
