import os
import json
import requests
from pathlib import Path

# ========================
# Azure AI Foundry Config
# ========================

API_KEY = os.environ["AZURE_FOUNDRY_API_KEY"]
ENDPOINT = os.environ["AZURE_FOUNDRY_ENDPOINT"]
DEPLOYMENT = os.environ["AZURE_FOUNDRY_DEPLOYMENT"]

OUTPUT_DIR = Path("analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)

LOG_FILE = "logs/openshift.log"

# ========================
# Read Log File
# ========================

with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
    log_content = f.read()

# Truncate huge logs
log_content = log_content[:100000]

# ========================
# Prompt
# ========================

SYSTEM_PROMPT = """
You are a Senior OpenShift Platform and Performance Engineer.

Analyze the OpenShift logs and provide:

## Executive Summary

## Critical Errors

## Pod Issues
- CrashLoopBackOff
- OOMKilled
- RestartCount

## Resource Utilization Findings
- Memory Issues
- CPU Issues
- Storage Issues

## Network Issues

## Root Cause Analysis

## Recommendations

Use markdown formatting.
"""

USER_PROMPT = f"""
Analyze the following OpenShift logs.

{log_content}
"""

# ========================
# Azure AI Foundry Call
# ========================

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "model": DEPLOYMENT,
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": USER_PROMPT
        }
    ],
    "temperature": 0.2,
    "max_tokens": 2500
}

response = requests.post(
    f"{ENDPOINT}/chat/completions",
    headers=headers,
    json=payload,
    timeout=120
)

response.raise_for_status()

analysis = response.json()["choices"][0]["message"]["content"]

# ========================
# Save Outputs
# ========================

with open(
    "analysis_output/summary.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(analysis)

with open(
    "analysis_output/summary.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        {
            "analysis": analysis
        },
        f,
        indent=2
    )

print("Analysis completed successfully.")
