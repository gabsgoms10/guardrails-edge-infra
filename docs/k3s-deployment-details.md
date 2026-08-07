# ☸️ Technical K3s Deployment Specification
## Edge Infrastructure — Repository `guardrails-edge-infra`

This document provides an in-depth technical breakdown of the topology, active components, resource constraints, and GitOps deployment strategy for the K3s cluster running on the **`saasdeploy`** edge node.

---

## 🖥️ 1. Infrastructure Node Specifications

- **Node Hostname**: `saasdeploy`
- **Cloud Provider**: Oracle Cloud Infrastructure (Always Free Tier)
- **CPU Architecture**: ARM64 (Ampere Altra Processor)
- **Total System Memory**: 12 GB RAM
- **Operating System**: Ubuntu Linux (Kernel 6.x)
- **Node Role**: Single-node Control Plane + Worker packaged

---

## 🔧 2. K3s Runtime & Control Plane Configuration

- **K3s Version**: `v1.36.3+k3s1`
- **Datastore Engine**: Embedded SQLite / Raft (<512MB RAM memory footprint for control plane)
- **Container Runtime**: `containerd` (natively integrated into K3s)
- **Kubeconfig Location**: `/etc/rancher/k3s/k3s.yaml` (Copied to `~/.kube/config` with non-root user `ubuntu` permissions)
- **Environment Variable**: `export KUBECONFIG=~/.kube/config` set in `~/.bashrc`

---

## 📦 3. Deployed Components & Namespace Setup (`namespace: guardrails`)

All microservices, policy engines, risk classifiers, and databases run strictly isolated within the Kubernetes **`guardrails`** namespace:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        NAMESPACE: guardrails                           │
│                                                                        │
│  ┌───────────────────────────┐      ┌───────────────────────────────┐  │
│  │ 🐘 PostgreSQL 16 Alpine   │      │ 🛡️ NeMo Guardrails Server    │  │
│  │ Service: postgres-service │      │ Service: nemo-service:8000    │  │
│  └───────────────────────────┘      └───────────────────────────────┘  │
│  ┌───────────────────────────┐      ┌───────────────────────────────┐  │
│  │ 🔬 Granite Guardian 2B    │      │ ⚡ FastMCP Server             │  │
│  │ Service: guardian:11434   │      │ Service: mcp-server:8001      │  │
│  └───────────────────────────┘      └───────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### 🔹 Component 3.1: PostgreSQL 16 Alpine (`postgres-service`)
- **Container Image**: `postgres:16-alpine`
- **Internal Port**: `5432` (ClusterIP internal service, not exposed publicly)
- **Resource Constraints**: `limits`: Memory `350Mi`, CPU `300m`
- **Idempotent Initialization (`/docker-entrypoint-initdb.d/init.sql`)**:
  - `characters` table: Bank account balances (Leo Vance, Maria Silva, Enterprise X Corp).
  - `blocked_pix_keys` table: BACEN fraud registry (`fraudster@pix.com`).
  - `transactions` table: Ledger transaction audit log.

### 🔹 Component 3.2: Granite Guardian 2B Classifier (`granite-guardian-service`)
- **Model**: IBM Granite 3.1 2B Guardian (Fine-tuned specialized risk classifier)
- **Role**: Local Binary Risk Classifier (`Yes`/`No` evaluation for Jailbreak, Harm, Off-topic & Groundedness)
- **Container Image**: `ollama/ollama:latest` (Serving GGUF quantized model)
- **Internal Port**: `11434` (ClusterIP internal service)
- **Resource Constraints**: `limits`: Memory `1800Mi`, CPU `1500m`
- **Architectural Advantage**: Evaluates input & output rails locally on the ARM node, consuming zero main LLM tokens and providing ultra-fast binary decisioning.

### 🔹 Component 3.3: NVIDIA NeMo Guardrails Server (`nemo-guardrails-service`)
- **Container Image**: `nemoguardrails/nemoguardrails:latest`
- **Internal Port**: `8000` (ClusterIP internal service)
- **Startup Command**: `nemoguardrails server --config /app/config`
- **Policy-as-Code**: Mounted via ConfigMap (`nemo-policy-config`) containing `config.yml` and `rails.co` (Colang v2 DSL).
- **Deployment Strategy**: `RollingUpdate` with `maxUnavailable: 0` and `maxSurge: 1` (Zero Downtime).
- **Readiness Probe**: HTTP GET check on `/v1/health` route every 5 seconds.

---

## 🔄 4. GitOps Automation & Self-Hosted Runner Integration

- **Runner Directory**: `~/actions-runner` on node `saasdeploy`.
- **System Daemon**: `systemd` (`actions.runner.guardrails-edge-infra.saasdeploy.service`).
- **Pipeline Workflow (`.github/workflows/deploy.yml`)**:
  1. Automatic trigger on `git push` to `main` branch.
  2. Executes `kubectl kustomize k3s/` to validate manifest syntax.
  3. Executes `kubectl apply -k k3s/` to deploy updates.
  4. Executes `kubectl rollout status` ensuring new pods pass readiness probes.

---

## 🔒 5. RAM Budget Allocation Summary (Oracle Cloud 12GB RAM Node)

| Component | Allocated RAM Limit | Role |
|---|---|---|
| K3s Control Plane + OS | ~2.0 GB | Lightweight Kubernetes runtime |
| NeMo Guardrails Server | ~1.2 GB | Policy engine (Colang v2 execution) |
| **Granite Guardian 2B Classifier** | **~1.8 GB** | Local Risk Classifier (Binary Yes/No) |
| PostgreSQL 16 Alpine | ~0.35 GB | Bank ledger & fraud registry database |
| FastMCP + Banking Agent | ~0.8 GB | MCP tool server & agentic loop |
| **System Headroom / Slack** | **~5.85 GB** | Unallocated headroom for traffic spikes |
| **Total System RAM** | **12.0 GB** | **100% within Free Tier Hardware Constraints** |
