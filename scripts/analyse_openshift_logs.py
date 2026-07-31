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
You are a Senior Performance Test Engineer with 15+ years of experience in analyzing OpenShift/Kubernetes application logs.

IMPORTANT RULES

1. DO NOT assume or fabricate information.
2. DO NOT calculate values that do not exist in logs.
3. If information is unavailable, write:
   Not Available in Logs.
4. Base observations strictly on log evidence.
5. Use markdown tables wherever possible.

Generate the report in EXACTLY the following format:

# OpenShift Performance Log Analysis Report

## 1. Executive Summary

## 2. Environment Information

## 3. Performance Observations

For every observation provide:

Finding:
Evidence from Logs:
Severity:
Impact:

## 4. API Performance Summary

| API Endpoint | HTTP Method | Response Code | Execution Time | Observations |

## 5. Exceptions Summary

| Exception | Count | Severity | Possible Cause |

## 6. Resource Related Findings

CPU

Memory

Heap

GC

Disk

Thread Pool

Connection Pool

## 7. Database Analysis

## 8. Pod Health Analysis

## 9. Timeline of Important Events

| Timestamp | Event | Severity |

## 10. Root Cause Analysis

## 11. Recommendations

## 12. Overall Assessment

## 13. Information Not Available

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

body{
    background:#eef7fc;
    font-family:"Segoe UI",Arial,sans-serif;
    margin:0;
    padding:30px;
    color:#2c3e50;
}

.container{
    max-width:1400px;
    margin:auto;
}

.header{
    background:linear-gradient(135deg,#5BBEF5,#2196F3);
    color:white;
    padding:30px;
    border-radius:15px;
    box-shadow:0 4px 15px rgba(0,0,0,.15);
}

.header h1{
    margin:0;
    font-size:32px;
}

.header p{
    margin-top:10px;
    font-size:15px;
    opacity:.95;
}

.report{
    background:white;
    padding:35px;
    margin-top:20px;
    border-radius:15px;
    box-shadow:0 4px 15px rgba(0,0,0,.08);
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:15px;
    margin-bottom:25px;
    overflow:hidden;
    border-radius:8px;
}

table,th,td{
    border:1px solid #d8ebf7;
}

th{
    background:#42A5F5;
    color:white;
    font-weight:600;
}

td{
    background:white;
}

tr:nth-child(even){
    background:#f8fcff;
}

th,td{
    padding:12px;
    text-align:left;
}

h1{
    margin-top:0;
}

h1,h2,h3{
    color:#1976D2;
}

h2{
    border-left:6px solid #42A5F5;
    padding-left:12px;
    margin-top:35px;
}

h3{
    margin-top:25px;
}

ul{
    line-height:1.8;
}

li{
    margin-bottom:6px;
}

code{
    background:#e8f4fd;
    padding:3px 6px;
    border-radius:5px;
    color:#1565C0;
}

pre{
    background:#f4faff;
    border-left:5px solid #42A5F5;
    padding:15px;
    overflow:auto;
    border-radius:8px;
}

blockquote{
    border-left:5px solid #42A5F5;
    background:#f7fbfe;
    margin:15px 0;
    padding:12px 18px;
    color:#555;
}

.footer{
    margin-top:25px;
    text-align:center;
    color:#607D8B;
    font-size:13px;
}

hr{
    border:none;
    border-top:1px solid #d8ebf7;
    margin:25px 0;
}

</style>
</head>

<body>

<div class="container">

<div class="header">
    <h1>🚀 OpenShift Performance Log Analysis Report</h1>
    <p>Generated using Azure AI Foundry</p>
</div>

<div class="report">

{html_report}

</div>

<div class="footer">
Generated Automatically Using Azure AI Foundry & GitHub Actions
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
