import os
import json
import requests
import markdown

from pathlib import Path

# ============================================================
# Azure AI Foundry Configuration
# ============================================================

API_KEY = os.environ["AZURE_FOUNDRY_API_KEY"]
ENDPOINT = os.environ["AZURE_FOUNDRY_ENDPOINT"]
DEPLOYMENT = os.environ["AZURE_FOUNDRY_DEPLOYMENT"]

# ============================================================
# Docs Folder
# ============================================================

DOCS = Path("docs")
DOCS.mkdir(exist_ok=True)

# ============================================================
# Read Log File
# ============================================================

with open(
    "logs/openshift.log",
    "r",
    encoding="utf-8",
    errors="ignore"
) as f:
    log_content = f.read()

log_content = log_content[:100000]

# ============================================================
# Prompt
# ============================================================

SYSTEM_PROMPT = """
You are a Senior Performance Test Engineer with 15+ years of experience in analyzing OpenShift/Kubernetes application logs, performance bottlenecks, JVM behavior, database connectivity, thread usage, and application stability.

Your task is to analyze ONLY the OpenShift console logs that I provide.

IMPORTANT RULES

1. DO NOT assume or fabricate any information.
2. DO NOT calculate values that are not present in the logs.
3. DO NOT invent CPU utilization, Memory utilization, Error Rate, TPS, Response Time averages, Pod Restart Count, OOMKilled events, or any performance metrics unless they explicitly exist in the logs.
4. If a metric is not available in the logs, clearly state:
   Not Available in Logs.
5. Base every observation strictly on evidence found in the logs.
6. Mention only findings that can be justified from the logs.
7. Ignore application functionality and focus on performance, stability, scalability, resource issues, and infrastructure observations.
8. Use markdown tables wherever applicable.

Generate the report in EXACTLY the following format.

# OpenShift Performance Log Analysis Report

## 1. Executive Summary

## 2. Environment Information

Extract if available:

- Namespace
- Pod Name
- Container Name
- Node Name
- Deployment
- Application Name
- OpenShift Cluster
- JVM Version
- Spring Boot Version
- Database
- Timestamp Range

If unavailable write:
Not Available in Logs

## 3. Performance Observations

For every observation provide:

Finding:
Evidence from Logs:
Severity:
Impact:

## 4. API Performance Summary

For each API provide:

| API Endpoint | HTTP Method | Response Code | Execution Time | Observations |

Do not calculate averages.

## 5. Exceptions Summary

| Exception | Count (Approximate if visible) | Severity | Possible Cause |

Only include exceptions actually present.

## 6. Resource Related Findings

CPU

Memory

Heap

GC

Disk

Thread Pool

Connection Pool

If unavailable write:
Not Available in Logs

## 7. Database Analysis

Only report database findings present in logs.

## 8. Pod Health Analysis

Only report if present:

- Pod Restarts
- OOMKilled
- CrashLoopBackOff
- Container Restart
- Node Failure

Otherwise write:

No pod health issues found in the provided logs.

## 9. Timeline of Important Events

| Timestamp | Event | Severity |

## 10. Root Cause Analysis

Based ONLY on log evidence.

If insufficient data exists write:

Root cause cannot be conclusively determined from the provided logs.

## 11. Recommendations

Only recommend actions related to identified issues.

## 12. Overall Assessment

Application Stability

Excellent
Good
Fair
Poor
Critical

Confidence Level

High
Medium
Low

Provide reason.

## 13. Information Not Available

List important metrics not present in logs.

Examples:

- Average Response Time
- P95 Response Time
- TPS
- Concurrent Users
- CPU Utilization
- Memory Utilization
- Heap Usage %
- GC Pause Time
- Pod Restart Count
- Prometheus Metrics
- Grafana Metrics
- OpenShift Monitoring Metrics

Return markdown only.
"""

# ============================================================
# Request Payload
# ============================================================

payload = {
    "model": DEPLOYMENT,
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": log_content
        }
    ],
    "temperature": 0.1,
    "max_tokens": 3500
}

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

# ============================================================
# Azure AI Foundry Call
# ============================================================

print("Calling Azure AI Foundry...")

response = requests.post(
    f"{ENDPOINT}/chat/completions",
    headers=headers,
    json=payload,
    timeout=180
)

response.raise_for_status()

analysis = response.json()["choices"][0]["message"]["content"]

print("Analysis received successfully.")

# ============================================================
# Save Markdown
# ============================================================

(DOCS / "summary.md").write_text(
    analysis,
    encoding="utf-8"
)

# ============================================================
# Save JSON
# ============================================================

(DOCS / "analysis.json").write_text(
    json.dumps(
        {
            "analysis": analysis
        },
        indent=2
    ),
    encoding="utf-8"
)

# ============================================================
# Markdown to HTML
# ============================================================

html_report = markdown.markdown(
    analysis,
    extensions=[
        "tables",
        "fenced_code",
        "nl2br"
    ]
)

# ============================================================
# HTML Dashboard
# ============================================================

html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="utf-8">

<title>OpenShift Performance Log Analysis Report</title>

<style>

body {{
    background:#f4f6f9;
    font-family:Segoe UI, Arial, sans-serif;
    margin:0;
    padding:30px;
}}

.container {{
    max-width:1400px;
    margin:auto;
}}

.header {{
    background:#c1121f;
    color:white;
    padding:25px;
    border-radius:12px;
}}

.report {{
    background:white;
    padding:30px;
    margin-top:20px;
    border-radius:12px;
    box-shadow:0 2px 10px rgba(0,0,0,.10);
}}

table {{
    width:100%;
    border-collapse:collapse;
    margin-top:15px;
    margin-bottom:20px;
}}

table, th, td {{
    border:1px solid #dcdcdc;
}}

th {{
    background:#c1121f;
    color:white;
}}

th, td {{
    padding:10px;
    text-align:left;
}}

h1 {{
    margin-top:0;
}}

h1, h2, h3 {{
    color:#c1121f;
}}

ul {{
    line-height:1.8;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>🚀 OpenShift Performance Log Analysis Report</h1>

<p>
Generated using Azure AI Foundry
</p>

</div>

<div class="report">

{html_report}

</div>

</div>

</body>

</html>
"""

(DOCS / "index.html").write_text(
    html,
    encoding="utf-8"
)

print("✅ summary.md created")
print("✅ analysis.json created")
print("✅ index.html created")
print("✅ Analysis completed successfully")
