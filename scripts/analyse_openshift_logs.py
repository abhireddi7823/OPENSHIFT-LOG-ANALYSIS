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
# Read OpenShift Logs
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
# AI Prompt
# ============================================================

SYSTEM_PROMPT = """
You are an experienced OpenShift Site Reliability Engineer (SRE), Kubernetes Administrator, Java Performance Engineer, and Performance Test Analyst.

Analyze the provided OpenShift application logs generated during performance testing.

The logs may contain activity from the following test types:
- Load Test
- Endurance Test
- Stress Test
- Spike Test

Your objective is to identify performance bottlenecks, application issues, infrastructure problems, and provide actionable recommendations.

Perform the following analysis:

1. Executive Summary
- Summarize the overall health of the application.
- Mention whether the system remained stable.
- Give an overall health score (0–100).

2. Test Phase Detection
Identify which sections belong to:
- Load Test
- Endurance Test
- Stress Test
- Spike Test

Explain why you classified them.

3. Error Analysis
Identify all errors including but not limited to:
- HTTP 500
- HTTP 503
- Database Connection Timeout
- SQL Connection Pool Exhaustion
- HikariPool Errors
- Java Exceptions
- OutOfMemoryError
- Liveness Probe Failure
- Readiness Probe Failure
- Container Restart
- Pod CrashLoopBackOff
- Node Issues
- Kubernetes Events

For every error provide:
- Timestamp
- Error Type
- Root Cause
- Impact
- Severity (Critical, High, Medium, Low)
- Recommended Fix

4. Performance Analysis

Analyze:
- Response Time
- Database Time
- CPU Utilization
- Memory Utilization
- Heap Usage
- Active Threads
- Thread Pool Usage
- GC Activity
- SQL Pool Usage
- JVM Health

Identify:
- Performance bottlenecks
- Slow APIs
- Resource saturation
- Thread starvation
- Memory leak indicators

5. Kubernetes/OpenShift Analysis

Analyze:
- Pod Restarts
- Autoscaling Events
- HPA Activity
- Liveness Probe Failures
- Readiness Probe Failures
- Container Restarts
- Scheduling Events
- Node Health

Explain whether the cluster behaved correctly.

6. SLA Analysis

Determine:
- APIs exceeding response time thresholds
- Average response time
- Peak response time
- Error percentage
- Availability observations

Highlight SLA violations.

7. Root Cause Analysis

Identify the top 5 issues affecting system performance.

For each issue include:
- Description
- Evidence from logs
- Business Impact
- Root Cause
- Recommended Resolution

8. Recommendations

Categorize recommendations into:

Immediate Actions
Short-Term Improvements
Long-Term Improvements

Include recommendations such as:
- Increase Hikari connection pool
- Optimize SQL queries
- Tune JVM heap
- Optimize Garbage Collection
- Increase pod replicas
- Adjust CPU and Memory requests/limits
- Improve autoscaling configuration
- Optimize thread pools
- Investigate memory leaks
- Improve application logging

9. Overall Risk Assessment

Provide:
- Stability Rating
- Performance Rating
- Scalability Rating
- Reliability Rating

Rate each from 1–10.

10. Final Report

Return the analysis in Markdown using the following format:

# OpenShift Performance Analysis Report

## Executive Summary

## Test Phase Summary

## Performance Metrics

## Errors Detected

| Timestamp | Severity | Error | Root Cause | Recommendation |

## Resource Utilization

## Kubernetes Events

## Performance Bottlenecks

## Root Cause Analysis

## Recommendations

## Risk Assessment

## Overall Health Score

Rules:
- Do not invent issues that are not present in the logs.
- Correlate related log events before determining a root cause.
- Explain every recommendation clearly.
- Highlight critical issues first.
- Use concise, professional language suitable for performance engineering and SRE teams.
- If the logs indicate normal behavior, explicitly state that no issue was detected.
Return markdown only.
"""

# ============================================================
# Azure AI Request
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
# Save Files
# ============================================================

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

# ============================================================
# Convert Markdown to HTML
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
# HTML Dashboard Template
# ============================================================

html_template = """
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

th,td{
    padding:12px;
    text-align:left;
}

h1,h2,h3{
    color:#1976D2;
}

h2{
    border-left:6px solid #42A5F5;
    padding-left:12px;
    margin-top:35px;
}

ul{
    line-height:1.8;
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

.footer{
    margin-top:25px;
    text-align:center;
    color:#607D8B;
    font-size:13px;
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

__REPORT__

</div>

<div class="footer">
Generated Automatically Using Azure AI Foundry &amp; GitHub Actions
</div>

</div>

</body>

</html>
"""

html = html_template.replace("__REPORT__", html_report)

(DOCS / "index.html").write_text(
    html,
    encoding="utf-8"
)

print("✅ summary.md created")
print("✅ analysis.json created")
print("✅ index.html created")
print("✅ Analysis completed successfully")
