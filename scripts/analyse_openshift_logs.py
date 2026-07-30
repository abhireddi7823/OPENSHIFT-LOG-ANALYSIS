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
You are a Principal OpenShift Performance Engineer.

Generate a professional report.

Use markdown tables.

Title:

# 🚀 OpenShift Log Analysis – Performance Test Report

Sections:

1. Document Control
2. Executive Summary
3. Test Objectives & Scope
4. System Under Test
5. Performance Scorecard
6. Critical Findings
7. Resource Utilization Analysis
8. Pod Health Analysis
9. Performance Metrics Analysis
10. Root Cause Analysis
11. Recommendations
12. Acceptance Criteria Summary
13. Final Verdict
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
