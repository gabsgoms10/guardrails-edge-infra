# 🐘 PostgreSQL Database & Schema Operations Guide
## Repository: `guardrails-edge-infra`

This guide explains how to connect to the PostgreSQL database inside the K3s cluster, inspect tables, and reset character balances.

---

## 🗄️ 1. Database Schema & Tables

All database objects are created automatically on pod startup via `/docker-entrypoint-initdb.d/init.sql` mounted from `postgres-seed` ConfigMap:

- **`characters`**: Holds test bank accounts (`Leo Vance`, `Maria Silva`, `Enterprise X Corp`).
- **`blocked_pix_keys`**: BACEN fraud registry (`fraudster@pix.com`, `night.fraud@pix.com`, `12345678900`).
- **`transactions`**: Audit log of approved and blocked PIX transfers.

---

## 🔌 2. Connecting to PostgreSQL inside K3s (SSH Terminal)

To run SQL queries directly on the node without installing `psql` locally:

```bash
# Connect directly to psql inside the running postgres pod
kubectl exec -it deployment/postgres -n guardrails -- psql -U guardrails_user -d guardrails_db
```

---

## 🛠️ 3. Useful Maintenance SQL Queries

```sql
-- 1. Check current character balances
SELECT name, pix_key, balance_cents / 100.0 AS balance_brl, risk_profile FROM characters;

-- 2. Check BACEN fraud registry list
SELECT * FROM blocked_pix_keys;

-- 3. Check transaction audit log
SELECT * FROM transactions ORDER BY criado_em DESC LIMIT 10;

-- 4. Reset balances back to initial test state
UPDATE characters SET balance_cents = 250000 WHERE name = 'Leo Vance';
UPDATE characters SET balance_cents = 4500000 WHERE name = 'Maria Silva';
UPDATE characters SET balance_cents = 12000000 WHERE name = 'Enterprise X Corp';
```
