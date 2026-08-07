# 🤖 GitHub Actions Self-Hosted Runner & CI/CD Operations Guide
## Repository: `guardrails-edge-infra`

This guide explains how the GitHub Actions self-hosted runner operates on the `saasdeploy` ARM64 node, how to manage systemd services, and how secrets are injected without hardcoding.

---

## ⚙️ 1. Self-Hosted Runner Service Overview

- **Host Machine**: `saasdeploy` (Oracle Cloud ARM64 VM)
- **Directory**: `~/actions-runner`
- **System Daemon**: `actions.runner.guardrails-edge-infra.saasdeploy.service`
- **Runner Group**: `Default`
- **Labels**: `self-hosted`, `Linux`, `ARM64`

---

## 🛠️ 2. Service Management Commands (SSH Terminal)

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

## 🔑 3. Managing GitHub Secrets for Deployment

No database passwords or API keys are committed to Git. The workflow `.github/workflows/deploy.yml` expects secrets to be set in your GitHub Repository:

### How to set Secrets in GitHub:
1. Go to your GitHub repository: `https://github.com/<YOUR_USER>/guardrails-edge-infra`
2. Navigate to **Settings** ➔ **Secrets and variables** ➔ **Actions**.
3. Click **New repository secret** and add:

| Secret Name | Example Value | Description |
|---|---|---|
| `POSTGRES_DB` | `guardrails_db` | PostgreSQL Database Name |
| `POSTGRES_USER` | `guardrails_user` | PostgreSQL Database User |
| `POSTGRES_PASSWORD` | `SecurePass2026!` | PostgreSQL Database Password |
| `OPENAI_API_KEY` | `sk-proj-...` | OpenAI API Key for NeMo Guardrails |

---

## 🔍 4. Troubleshooting & Inspection Commands

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
