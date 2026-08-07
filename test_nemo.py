import sys
import yaml

with open("k3s/nemo-guardrails/configmap-policy.yaml", encoding="utf-8") as f:
    docs = list(yaml.safe_load_all(f))

configmap = docs[0]
config_yml = yaml.safe_load(configmap["data"]["config.yml"])
models = config_yml.get("models", [])
for m in models:
    print(m)
