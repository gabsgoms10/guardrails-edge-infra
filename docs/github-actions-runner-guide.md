# 🤖 GitHub Actions Self-Hosted Runner & CI/CD Operations Guide
## Repository: `guardrails-edge-infra`

This guide explains how the GitHub Actions self-hosted runner operates on the `saasdeploy` ARM64 node, how to manage systemd services, and how automated post-deployment integration tests run.

---

## ⚙️ 1. Self-Hosted Runner Service Overview

- **Host Machine**: `saasdeploy` (Oracle Cloud ARM64 VM)
- **Directory**: `~/actions-runner`
- **System Daemon**: `actions.runner.guardrails-edge-infra.saasdeploy.service`
- **Runner Group**: `Default`
- **Labels**: `self-hosted`, `Linux`, `ARM64`

---

## 🧪 2. Automated Post-Deployment Integration Tests

Every CI/CD execution automatically runs a post-deploy verification step before marking the pipeline as green:

1. 🐘 **PostgreSQL DB Integrity Test**: Executes `SELECT count(*) FROM characters;` inside the cluster.
2. 🔬 **Granite Guardian 2B Health Check**: Sends an internal HTTP ping to `http://granite-guardian-service.guardrails.svc.cluster.local:11434/api/tags`.
3. 🛡️ **NeMo Guardrails Server Health Check**: Sends an internal HTTP ping to `http://nemo-guardrails-service.guardrails.svc.cluster.local:8000/v1/health`.

---

## 🛠️ 3. Service Management Commands (SSH Terminal)

If you ever need to check, restart, or troubleshoot the GitHub Actions daemon on your VM:

```bash
cd ~/actions-runner

# Check background daemon status
sudo ./svc.sh status

# Start service
sudo ./svc.sh start

# Stop service
sudo ./svc.sh stop

# Uninstall service (if re-registering)
sudo ./svc.sh uninstall
```

---

## 🔑 4. Managing GitHub Secrets for Deployment

No database passwords or API keys are committed to Git. The workflow `.github/workflows/deploy.yml` expects secrets to be set in your GitHub Repository:

### How to set Secrets in GitHub:
1. Go to your GitHub repository: `https://github.com/<YOUR_USER>/guardrails-edge-infra`
2. Navigate to **Settings** ➔ **Secrets and variables** ➔ **Actions**.
3. Click **New repository secret** and add `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

---

## 🔍 5. Troubleshooting & Inspection Commands

If a GitHub Actions deployment fails or hangs:

```bash
# Check pod rollout status in K3s
kubectl get pods -n guardrails -o wide

# View logs for a specific pod
kubectl logs -l app=postgres -n guardrails
kubectl logs -l app=nemo-guardrails -n guardrails
kubectl logs -l app=granite-guardian -n guardrails

# Describe pod events (useful for image pull or resource limits)
kubectl describe pod -l app=postgres -n guardrails
```
