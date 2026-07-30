import os
import json
import requests
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

SYSTEM_PROMPT = """
You are a Senior OpenShift Performance Engineer.

Analyse the logs and provide:

# Executive Summary

# Performance Score
Provide score out of 100.

# Critical Findings

# Resource Findings

# Root Cause Analysis

# Recommendations

# Severity
Critical / High / Medium / Low

Return markdown.
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
    "max_tokens": 2500
}

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(
    f"{ENDPOINT}/chat/completions",
    headers=headers,
    json=payload,
    timeout=120
)

response.raise_for_status()

analysis = response.json()["choices"][0]["message"]["content"]

(Path("docs") / "summary.md").write_text(
    analysis,
    encoding="utf-8"
)

(Path("docs") / "analysis.json").write_text(
    json.dumps(
        {
            "analysis": analysis
        },
        indent=2
    ),
    encoding="utf-8"
)

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>OpenShift Log Analysis</title>

<style>

body {{
font-family: Arial, sans-serif;
background:#f4f6f9;
padding:40px;
margin:0;
}}

.container {{
background:white;
padding:30px;
border-radius:10px;
box-shadow:0 2px 10px rgba(0,0,0,0.2);
}}

h1 {{
color:#c1121f;
}}

pre {{
white-space: pre-wrap;
word-wrap: break-word;
font-size:14px;
line-height:1.6;
}}

</style>

</head>
<body>

<div class="container">

<h1>🚀 OpenShift AI Log Analysis</h1>

<p>
Generated using Azure AI Foundry
</p>

<pre>
{analysis}
</pre>

</div>

</body>
</html>
"""

(Path("docs") / "index.html").write_text(
    html,
    encoding="utf-8"
)

print("Analysis completed successfully.")
