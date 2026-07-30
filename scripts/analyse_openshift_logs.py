import os
import json
import requests
import markdown

from pathlib import Path

API_KEY = os.environ["AZURE_FOUNDRY_API_KEY"]
ENDPOINT = os.environ["AZURE_FOUNDRY_ENDPOINT"]
DEPLOYMENT = os.environ["AZURE_FOUNDRY_DEPLOYMENT"]

DOCS = Path("docs")
DOCS.mkdir(exist_ok=True)

with open("logs/openshift.log", "r", encoding="utf-8", errors="ignore") as f:
    log_content = f.read()

SYSTEM_PROMPT = """
You are a Senior Performance Test Engineer with 15+ years of experience in analyzing OpenShift/Kubernetes application logs, performance bottlenecks, JVM behavior, database connectivity, thread usage, and application stability.

Your task is to analyze ONLY the OpenShift console logs that I provide.

IMPORTANT RULES:

1. DO NOT assume or fabricate any information.
2. DO NOT calculate values that are not present in the logs.
3. DO NOT invent CPU utilization, Memory utilization, Error Rate, TPS, Response Time averages, Pod Restart Count, OOMKilled events, or any performance metrics unless they explicitly exist in the logs.
4. If a metric is not available in the logs, clearly state:
   "Not Available in Logs".
5. Base every observation strictly on evidence found in the logs.
6. Think exactly like a Senior Performance Engineer performing a production log analysis.
7. Mention only findings that can be justified from the logs.
8. Ignore application functionality and focus on performance, stability, scalability, resource issues, and infrastructure-related observations.

Analyze the logs and generate the report in the following format.

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

If not found:
Not Available in Logs

## 3. Performance Observations

For every finding include:

Finding:
Evidence from Logs:
Severity:
Impact:

## 4. API Performance Summary

Extract every API found in logs.

For each API provide:

- API Endpoint
- HTTP Method
- Response Code
- Execution Time
- Observations

Do NOT calculate averages.

## 5. Exceptions Summary

Create markdown table.

| Exception | Count | Severity | Possible Cause |

## 6. Resource Related Findings

CPU

Memory

Heap

GC

Disk

Thread Pool

Connection Pool

If unavailable:
Not Available in Logs

## 7. Database Analysis

## 8. Pod Health Analysis

Only report if present.

## 9. Timeline of Important Events

| Timestamp | Event | Severity |

## 10. Root Cause Analysis

Based ONLY on evidence in logs.

If insufficient:

Root cause cannot be conclusively determined from the provided logs.

## 11. Recommendations

Provide recommendations only for issues identified.

## 12. Overall Assessment

Application Stability

Excellent / Good / Fair / Poor / Critical

Confidence Level

High / Medium / Low

Include reason.

## 13. Information Not Available

List performance metrics that cannot be determined from logs.

Remember:

Only report what is supported by the logs.

Never invent values.

If missing write:

Not Available in Logs.
"""

payload = {
    "model": DEPLOYMENT,
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": log_content[:100000]
        }
    ],
    "temperature": 0.2,
    "max_tokens": 3500
}

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(
    f"{ENDPOINT}/chat/completions",
    headers=headers,
    json=payload,
    timeout=180
)

response.raise_for_status()

analysis = response.json()["choices"][0]["message"]["content"]

(DOCS / "summary.md").write_text(
    analysis,
    encoding="utf-8"
)

(DOCS / "analysis.json").write_text(
    json.dumps(
        {
            "analysis": analysis
        },
        indent=2
    ),
    encoding="utf-8"
)

html_body = markdown.markdown(
    analysis,
    extensions=["tables"]
)

html = f"""
<!DOCTYPE html>
<html>

<head>

<meta charset="utf-8">

<title>OpenShift Log Analysis</title>

<style>

body {{
background:#f4f6f9;
font-family:Segoe UI;
padding:30px;
}}

.container {{
max-width:1400px;
margin:auto;
}}

.header {{
background:#c1121f;
color:white;
padding:20px;
border-radius:10px;
}}

.report {{
background:white;
padding:30px;
margin-top:20px;
border-radius:10px;
box-shadow:0 2px 10px rgba(0,0,0,.1);
}}

table {{
border-collapse:collapse;
width:100%;
}}

table,th,td {{
border:1px solid #ddd;
}}

th {{
background:#c1121f;
color:white;
}}

th,td {{
padding:10px;
}}

h1,h2,h3 {{
color:#c1121f;
}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>🚀 OpenShift Log Analysis Performance Report</h1>

<p>Generated using Azure AI Foundry</p>

</div>

<div class="report">

{html_body}

</div>

</div>

</body>

</html>
"""

(DOCS / "index.html").write_text(
    html,
    encoding="utf-8"
)

print("Analysis completed successfully")
