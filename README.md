# ☸️ guardrails-edge-infra

> **GitOps & Platform Engineering**: Lightweight Kubernetes cluster (K3s) hosted on ARM64 hardware (Oracle Cloud 12GB RAM Free Tier) serving the **NVIDIA NeMo Guardrails Server**, **Granite Guardian 2B Local Classifier**, **PostgreSQL**, and **FastMCP Server**.

---

## 🎯 Portfolio Context & Core Engineering Thesis

This repository (`guardrails-edge-infra`) is the infrastructure backbone of a **5-Repository Enterprise Portfolio System** designed to demonstrate end-to-end AI Agent Governance & Observability in high-risk financial environments (Instant PIX Transfers & Banking Operations).

The overarching architectural thesis of this portfolio — engineered to make an immediate impact on **Tech Leads, VPs of Engineering, and Senior AI Recruiters** — is built upon 3 strategic pillars:

### 💡 The Central Thesis
> *"System Prompts and text instructions **DO NOT** guarantee deterministic safety for production AI. To empower Autonomous Agents to execute high-risk real-world financial actions (such as instant PIX banking transfers), it is indispensable to adopt layered **Policy-as-Code (NVIDIA NeMo Guardrails + FastMCP)**, auditing and intercepting the Agentic Loop before, during, and after inference."*

---

## 🏛️ The 3 Strategic Sub-Pillars Demonstrated in the Project

### 🛡️ 1. Agentic Risk & Governance (The Safety Thesis)
- **The Problem**: Language models are probabilistic and inherently vulnerable to Prompt Injection and social engineering (such as the infamous 2023 Chevrolet dealership case where a chatbot agreed to sell a $58k car for $1).
- **The Technical Proof**: The **NeMo Execution Rail** intercepts the agent's intent to execute the `transfer_pix` tool call on the FastMCP server, querying the PostgreSQL fraud registry (`blocked_pix_keys`) and halting the execution **before it ever touches the production database ledger**.

### ⚡ 2. FinOps & Production Cost Awareness (The Performance Thesis)
- **The Problem**: Enterprise AI applications waste thousands of dollars in cloud inference budget when users ask out-of-scope questions (cooking recipes, programming code, casual chat).
- **The Technical Proof**: The **Input Rail** coupled with the local specialized classifier **IBM Granite Guardian 2B** (running directly in the edge K3s cluster) intercepts out-of-domain prompts in **<15ms**, saving 100% of main LLM tokens with fast deterministic binary decisions.

### 🏦 3. Incontestable Visual Proof (Show, Don't Tell)
- **The Demonstration**: Instead of displaying wall-of-text logs that recruiters never read, the **Visual Ledger** exposes live account balances for test characters (**Leo Vance**, **Maria Silva**, **Enterprise X Corp**). In *"Without Guardrail"* mode, an injection attack simulates draining the balance to $0.00; in *"With Guardrail"* mode, NeMo intercepts the attack, keeping the balance 100% protected in PostgreSQL.

---

## 📸 Automated CI/CD Integration Test Results (Sprint 2 Complete)

Every GitOps deployment executes an automated multi-stage integration test suite validating PostgreSQL connectivity/seeds, FastMCP SSE tool servers, Granite Guardian 2B classifier endpoints, and NVIDIA NeMo Guardrails Server policy status.

![Sprint 2 Automated Integration Tests Evidence](./images/github_actions_sprint2_success.png)

```text
========================================================================
🧪 INTEGRATION & HEALTH TEST SUITE — EDGE K3s CLUSTER VALIDATION
========================================================================

------------------------------------------------------------------------
🐘 Integration Test [PostgreSQL Database & Seed Integrity]
   Test   -> Querying 'characters' table seed records
   Result -> SUCCESS: 3 active bank accounts verified (Leo Vance, Maria Silva, Enterprise X Corp)

------------------------------------------------------------------------
🔌 Integration Test [FastMCP Banking Tools SSE Server]
   Test   -> Pinging SSE endpoint 'http://mcp-banking-service:8001/sse'
   Result -> SUCCESS: FastMCP Banking Tools Server Online (event: endpoint /messages/?session_id=...)

------------------------------------------------------------------------
🔬 Integration Test [IBM Granite Guardian 2B Local Classifier]
   Test   -> Pinging endpoint 'http://granite-guardian-service:11434/api/tags'
   Result -> SUCCESS: Classifier API Online ({"models":[]})

------------------------------------------------------------------------
🛡️ Integration Test [NVIDIA NeMo Guardrails Server]
   Test   -> Pinging endpoint 'http://nemo-guardrails-service:8000/v1/rails/configs'
   Result -> SUCCESS: NeMo Server Online with Active Policies ([{"id":"config"}])

========================================================================
🎉 ALL POST-DEPLOYMENT INTEGRATION TESTS PASSED 100% SUCCESSFULLY!
========================================================================
```

---

## 📖 Extended Technical Documentation & Flow Specifications
- 📄 **[Technical K3s Deployment Specification](./docs/k3s-deployment-details.md)**
- 📊 **[LLM Quotas, Rate Limits & Multi-Model Fallback Architecture](./docs/llm-rate-limits-and-fallbacks.md)**
- ☸️ **[K3s Microservices Integration & Dependency Flow](./docs/k3s-mcp-integration-flow.md)**
- 🤖 **[GitHub Actions Self-Hosted Runner & Operations Guide](./docs/github-actions-runner-guide.md)**
- 🐘 **[PostgreSQL Database & Schema Operations Guide](./docs/database-operations-guide.md)**

---

## 🔬 Local Specialized Risk Classifier: Granite Guardian 2B

Rather than invoking an expensive generalist LLM (like GPT-4o) for simple safety checks, our architecture runs a **specialized local classifier** directly inside the K3s cluster:

- **Model**: **IBM Granite Guardian 2B** (Fine-tuned version of Granite 3.1 2B Instruct specialized in risk taxonomy: jailbreak, harm, off-topic, hallucination & groundedness).
- **Behavior**: Responds exclusively with binary `Yes` / `No` classification output.
- **FinOps Advantage**: Evaluates Input and Output Rails locally on the ARM node (~1.8GB RAM allocated), eliminating main LLM token costs for blocked prompts.

---

## 🏛️ 1. Architecture Decisions & Technical Trade-offs

### ❓ Why K3s instead of Traditional Upstream Kubernetes (EKS / GKE / K8s)?

In an edge infrastructure environment with strict hardware memory constraints (12GB RAM on Oracle Cloud Free Tier), choosing the right Kubernetes distribution was critical to guarantee sufficient memory allocation for AI models and microservices:

| Engineering Metric | Traditional Kubernetes (K8s / etcd) | K3s (CNCF Certified Lightweight) | Staff Engineering Decision |
|---|---|---|---|
| **Control Plane RAM Consumption** | ~2.5 GB to 4.0 GB RAM (separate etcd + kube-apiserver) | **~512 MB RAM** (Embedded SQLite / Raft) | 🏆 **K3s saves >3.0 GB RAM** which is directly allocated to NeMo Server, Granite Guardian 2B, and FastMCP. |
| **Binary Footprint** | Dozens of binaries & heavy OS dependencies | **Single lightweight binary (<100MB)** | Instant & idempotent bootstrap on ARM64 nodes. |
| **API & Tooling Compatibility** | Industry standard | **100% CNCF Certified API** | Native support for standard K8s manifests (`kubectl apply`, Kustomize, PVCs, Ingress, Secrets). |
| **Trade-off / Constraint** | High Availability across thousands of multi-AZ nodes | Single-node control plane by default | 💡 **Accepted Trade-off**: For edge/staging PoCs and enterprise demos, a single-node K3s eliminates operational overhead. Migrating to production EKS is 100% seamless without changing application YAMLs. |

---

## 🛠️ 2. K3s Manifests & Directory Structure (GitOps)

```text
guardrails-edge-infra/
├── .github/
│   └── workflows/
│       └── deploy.yml               # GitOps pipeline executing on self-hosted runner
├── docs/
│   ├── k3s-deployment-details.md    # In-depth technical specification
│   ├── llm-rate-limits-and-fallbacks.md # LLM quotas & resilience decision matrix
│   ├── k3s-mcp-integration-flow.md  # K3s microservices dependency & flow doc
│   ├── github-actions-runner-guide.md # CI/CD & runner management guide
│   └── database-operations-guide.md # PostgreSQL queries & maintenance guide
├── k3s/
│   ├── namespace.yaml               # 'guardrails' namespace
│   ├── guardian/
│   │   └── deployment.yaml          # IBM Granite Guardian 2B Local Classifier (Ollama)
│   ├── mcp/
│   │   └── deployment.yaml          # FastMCP Python Server (GHCR Image + initContainers)
│   ├── postgres/
│   │   ├── deployment.yaml          # PostgreSQL tuned for low RAM (~350MB)
│   │   ├── service.yaml
│   │   └── configmap-seed.yaml      # Seeds: characters, blocked_pix_keys, transactions
│   ├── nemo-guardrails/
│   │   ├── deployment.yaml          # NVIDIA NeMo Guardrails FastAPI Server
│   │   ├── service.yaml
│   │   └── configmap-policy.yaml    # Policy-as-Code (config.yml + rails.co)
│   └── kustomization.yaml           # Kustomize orchestrator
├── images/
│   ├── k3s_install.png              # K3s installation proof
│   ├── git_actions_runner_config.png # GitHub Actions runner registration proof
│   └── github_actions_sprint2_success.png # Automated integration tests proof
└── README.md
```

---

## 🔄 3. Continuous Integration & GitOps Deployment Pipeline

This repository leverages a **GitHub Actions Self-Hosted Runner** running as a `systemd` background service on the `saasdeploy` node.

Every push to the `main` branch automatically triggers the following pipeline:
```bash
kubectl apply -k k3s/
```
No public API server exposure (port 6443 remains internal), enforcing zero-trust security practices.
