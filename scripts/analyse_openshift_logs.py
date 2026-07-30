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

with open(
    "logs/openshift.log",
    "r",
    encoding="utf-8",
    errors="ignore"
) as f:
    log_content = f.read()

log_content = log_content[:100000]

SYSTEM_PROMPT = """
You are a Principal Performance Engineer.

Generate a professional OpenShift Performance Test Report.

IMPORTANT:

Use markdown tables.

Example:

| Field | Value |
|--------|--------|
| Report Name | OpenShift Performance Analysis |

DO NOT output plain text tables.

Return markdown only.

# 🚀 OpenShift Log Analysis – Performance Test Report

## 1. Document Control

## 2. Executive Summary

## 3. Test Objectives & Scope

## 4. System Under Test (SUT)

Provide markdown table.

## 5. Performance Scorecard

Provide markdown table.

## 6. Critical Findings

Provide markdown table.

## 7. Resource Utilization Analysis

### CPU Analysis

### Memory Analysis

### Network Analysis

### Storage Analysis

## 8. Pod Health Analysis

Provide markdown table.

## 9. Performance Metrics Analysis

## 10. Root Cause Analysis

## 11. Recommendations

### Immediate Actions

### Short-Term Improvements

### Long-Term Improvements

## 12. Acceptance Criteria Summary

Provide markdown table.

## 13. Final Verdict

✅ PASS

⚠ PASS WITH OBSERVATIONS

❌ FAIL
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
            "content": log_content
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

html_report_body = markdown.markdown(
    analysis,
    extensions=[
        "tables",
        "fenced_code"
    ]
)

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">

<title>OpenShift Log Analysis Performance Report</title>

<style>

body {{
    font-family: Segoe UI, Arial, sans-serif;
    background:#f5f7fa;
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
    margin-top:20px;
    padding:30px;
    border-radius:12px;
    box-shadow:0 2px 10px rgba(0,0,0,.1);
}}

table {{
    width:100%;
    border-collapse:collapse;
    margin-bottom:20px;
}}

th {{
    background:#c1121f;
    color:white;
}}

th, td {{
    border:1px solid #ddd;
    padding:10px;
}}

h1,h2,h3 {{
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
<h1>🚀 OpenShift Log Analysis – Performance Test Report</h1>
<p>Generated using Azure AI Foundry</p>
</div>

<div class="report">

{html_report_body}

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
