# Incident Predictor ML - Deployment Guide

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites](#prerequisites)
3. [Architecture Overview](#architecture-overview)
4. [Local Development Setup](#local-development-setup)
5. [Docker Deployment](#docker-deployment)
6. [Production Deployment Options](#production-deployment-options)
7. [Configuration Reference](#configuration-reference)
8. [Integration Points](#integration-points)
9. [Monitoring & Observability](#monitoring--observability)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)
12. [Rollback Procedures](#rollback-procedures)

---

## Executive Summary

The Incident Predictor ML system transforms your incident replay tool into a **predictive incident detection engine** that catches infrastructure issues **6-20 minutes before they escalate**. This deployment guide provides comprehensive instructions for deploying, configuring, and maintaining the prediction engine in production environments.

### Key Capabilities

- **Predictive Detection**: Catches incidents 6-20 minutes early using Z-score anomaly detection + Isolation Forest ML
- **High Confidence Alerting**: Only alerts when 80%+ confident (minimizes alert fatigue)
- **Multi-Metric Support**: CPU, memory, disk, network, errors, latency
- **SDF Integration**: Pushes predictions to Security Data Fabric Gold layer
- **Zero External ML Costs**: Runs entirely on scikit-learn + numpy

### Performance Targets

- **Detection Cycle**: < 2 seconds per cycle
- **False Positive Rate**: < 5%
- **Early Warning Window**: 6-20 minutes
- **Confidence Threshold**: 80%+

---

## Prerequisites

### Required

- **Python 3.11+** (for local development)
- **Docker 20.10+** and **Docker Compose 2.0+** (for containerized deployment)
- **2 CPU cores** and **512MB RAM** minimum per instance
- **Network access** to:
  - Dynatrace API (metrics source)
  - Security Data Fabric Gold layer (prediction sink)
  - Internal monitoring systems

### Optional

- **Kubernetes cluster** (AKS, EKS, GKE) for orchestrated deployment
- **Azure Key Vault** or equivalent for secrets management
- **Prometheus** + **Grafana** for metrics visualization
- **Splunk/OpenSearch** for log aggregation

---

## Architecture Overview

```
┌─────────────────┐
│  Dynatrace API  │ ← Metrics source (CPU, memory, disk, network)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│          Incident Predictor ML Engine           │
│                                                  │
│  ┌────────────────┐    ┌──────────────────┐    │
│  │ Anomaly        │    │ Trajectory       │    │
│  │ Detector       │───▶│ Predictor        │    │
│  │ (Z-score + IF) │    │ (Linear Extrap)  │    │
│  └────────────────┘    └──────────────────┘    │
│                              │                   │
│                              ▼                   │
│                    ┌──────────────────┐         │
│                    │ Confidence       │         │
│                    │ Filter (>80%)    │         │
│                    └──────────────────┘         │
└───────────────────────────┬─────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Security Data Fabric    │
              │ (Gold Layer)            │
              └─────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    ┌──────────────────┐      ┌──────────────────┐
    │ ServiceNow       │      │ PagerDuty        │
    │ (Auto-ticket)    │      │ (Alert on-call)  │
    └──────────────────┘      └──────────────────┘
```

### Components

1. **Anomaly Detector** (`src/prediction/anomaly_detector.py`)
   - Z-score baseline analysis
   - Isolation Forest ML model
   - Multi-metric support
   - Configurable severity thresholds

2. **Trajectory Predictor** (`src/prediction/trajectory_predictor.py`)
   - Linear trajectory extrapolation
   - Time-to-breach calculation
   - Confidence scoring
   - Prediction type classification

3. **SDF Bridge** (`src/integration/sdf_bridge.py`)
   - Security Data Fabric integration
   - Batch push support
   - Retry logic with exponential backoff
   - Event formatting

4. **Main Loop** (`src/main.py`)
   - Orchestrates detection cycles
   - Configurable interval (default 60s)
   - Async/await architecture
   - Graceful shutdown handling

---

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/EPdacoder05/incident-replay-tool.git
cd incident-replay-tool
```

### Step 2: Install Dependencies

**Using Poetry (recommended):**

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

**Using pip:**

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Or manually:
pip install numpy scikit-learn pandas httpx pydantic pydantic-settings pytest pytest-asyncio
```

### Step 3: Run Local Validation

```bash
# Run validation suite
python tests/validate_local.py

# Expected output:
# ============================================================
# INCIDENT PREDICTOR ML - LOCAL VALIDATION SUITE
# ============================================================
# 
# === Test 1: Normal Metrics → 0 Alerts ===
# ✅ PASS: No false positives detected
# 
# === Test 2: CPU Spike Detection ===
# ✅ PASS: CPU spike detected with appropriate confidence and ETA
# ...
# Tests passed: 7/7
# 🎉 ALL TESTS PASSED - Ready for deployment
```

### Step 4: Run Main Prediction Loop (Mock Mode)

```bash
# Run with mock data
export MOCK_MODE=true
export DETECTION_INTERVAL_SECONDS=60

python -m src.main

# Expected output:
# [Incident Predictor ML] Initializing...
#   - Detection interval: 60s
#   - Mock mode: true
# [Incident Predictor ML] Using mock Dynatrace API
# [Incident Predictor] Starting prediction loop (interval: 60s)
# 
# [Incident Predictor] === Cycle 1 ===
# [Incident Predictor] Cycle completed in 145.23ms
#   - Metrics checked: 4
#   - Anomalies detected: 1
#   - Predictions generated: 1
#   - High-confidence predictions: 1
```

---

## Docker Deployment

### Quick Start (One Command Demo)

```bash
# Build and run with docker-compose
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f incident-predictor

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t incident-predictor-ml:latest .

# Run container
docker run -d \
  --name incident-predictor \
  -e DETECTION_INTERVAL_SECONDS=60 \
  -e MOCK_MODE=true \
  -v $(pwd)/logs:/app/logs \
  incident-predictor-ml:latest

# View logs
docker logs -f incident-predictor

# Stop container
docker stop incident-predictor
docker rm incident-predictor
```

---

## Production Deployment Options

### Option 1: Azure Kubernetes Service (AKS) - Recommended

**Pros:**
- Auto-scaling based on load
- High availability (multi-replica)
- Seamless updates with rolling deployments
- Native Azure integrations (Key Vault, Monitor)

**Cost:** ~$300-500/month (3-node cluster, Standard_D2s_v3)

**Deployment Steps:**

1. **Create AKS cluster:**

```bash
az aks create \
  --resource-group rg-incident-predictor \
  --name aks-incident-predictor \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --generate-ssh-keys
```

2. **Get cluster credentials:**

```bash
az aks get-credentials \
  --resource-group rg-incident-predictor \
  --name aks-incident-predictor
```

3. **Create Kubernetes manifests:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: incident-predictor
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: incident-predictor
  template:
    metadata:
      labels:
        app: incident-predictor
    spec:
      containers:
      - name: predictor
        image: yourregistry.azurecr.io/incident-predictor-ml:latest
        env:
        - name: DETECTION_INTERVAL_SECONDS
          value: "60"
        - name: MOCK_MODE
          value: "false"
        - name: SDF_API_KEY
          valueFrom:
            secretKeyRef:
              name: sdf-credentials
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30
```

4. **Deploy:**

```bash
kubectl apply -f deployment.yaml
kubectl get pods -n monitoring
```

### Option 2: Azure App Service (Container)

**Pros:**
- Fully managed (no cluster management)
- Built-in SSL certificates
- Easy CI/CD with GitHub Actions
- Cost-effective for single instance

**Cost:** ~$70-150/month (B2/B3 tier)

**Deployment Steps:**

```bash
# Create App Service Plan
az appservice plan create \
  --name asp-incident-predictor \
  --resource-group rg-incident-predictor \
  --is-linux \
  --sku B2

# Create Web App for Containers
az webapp create \
  --resource-group rg-incident-predictor \
  --plan asp-incident-predictor \
  --name app-incident-predictor \
  --deployment-container-image-name yourregistry.azurecr.io/incident-predictor-ml:latest

# Configure environment variables
az webapp config appsettings set \
  --resource-group rg-incident-predictor \
  --name app-incident-predictor \
  --settings \
    DETECTION_INTERVAL_SECONDS=60 \
    MOCK_MODE=false \
    SDF_ENDPOINT=https://sdf-gold.internal/api/events
```

### Option 3: Docker on Azure VMs

**Pros:**
- Full control over environment
- No orchestration complexity
- Direct access for debugging

**Cost:** ~$50-100/month (Standard_B2s VM)

**Deployment Steps:**

```bash
# Create VM
az vm create \
  --resource-group rg-incident-predictor \
  --name vm-incident-predictor \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH into VM
ssh azureuser@<vm-ip-address>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Deploy with docker-compose
git clone https://github.com/EPdacoder05/incident-replay-tool.git
cd incident-replay-tool
docker-compose up -d --build
```

### Cost Comparison

| Option | Monthly Cost | Pros | Best For |
|--------|-------------|------|----------|
| AKS | $300-500 | Auto-scaling, HA | Enterprise, high-traffic |
| App Service | $70-150 | Managed, simple | Mid-size, moderate traffic |
| VM + Docker | $50-100 | Full control | Small teams, testing |

---

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DETECTION_INTERVAL_SECONDS` | No | `60` | Seconds between detection cycles |
| `MOCK_MODE` | No | `true` | Use mock data instead of real API |
| `SDF_ENDPOINT` | No | `https://sdf-gold.internal/api/events` | SDF API endpoint |
| `SDF_API_KEY` | Yes (prod) | None | SDF API authentication key |
| `DYNATRACE_API_URL` | Yes (prod) | None | Dynatrace API base URL |
| `DYNATRACE_API_TOKEN` | Yes (prod) | None | Dynatrace API token |
| `MIN_CONFIDENCE` | No | `80.0` | Minimum confidence threshold (%) |
| `MAX_PREDICTION_WINDOW_MINUTES` | No | `30` | Maximum prediction time window |
| `BASELINE_WINDOW_HOURS` | No | `24` | Hours of baseline data |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Example .env File

```bash
# Prediction Engine Configuration
DETECTION_INTERVAL_SECONDS=60
MOCK_MODE=false
MIN_CONFIDENCE=80.0

# SDF Integration
SDF_ENDPOINT=https://sdf-gold.internal/api/events
SDF_API_KEY=your-sdf-api-key-here

# Dynatrace Integration
DYNATRACE_API_URL=https://your-tenant.live.dynatrace.com/api/v2
DYNATRACE_API_TOKEN=your-dynatrace-token-here

# Logging
LOG_LEVEL=INFO
```

**Security Note:** Never commit `.env` files to version control. Use Azure Key Vault or equivalent for secrets management in production.

---

## Integration Points

### 1. Dynatrace REST API

**Purpose:** Fetch real-time metrics for anomaly detection

**Authentication:** API Token with `metrics.read` permission

**Sample API Call:**

```python
import httpx

async def fetch_dynatrace_metrics():
    headers = {"Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"}
    
    response = await httpx.get(
        f"{DYNATRACE_API_URL}/metrics/query",
        headers=headers,
        params={
            "metricSelector": "builtin:host.cpu.usage",
            "resolution": "5m",
            "from": "now-1h"
        }
    )
    
    return response.json()
```

**Metrics to Query:**

- `builtin:host.cpu.usage` - CPU utilization
- `builtin:host.mem.usage` - Memory utilization
- `builtin:host.disk.usedPct` - Disk utilization
- `builtin:host.net.nic.trafficPct` - Network utilization

### 2. Security Data Fabric (SDF)

**Purpose:** Push predictions as enriched security events

**Authentication:** Bearer token

**Event Format:**

```json
{
  "event_type": "predictive_incident_alert",
  "timestamp": "2026-02-06T23:21:38Z",
  "severity": "critical",
  "source": "incident-predictor-ml",
  "prediction": {
    "type": "cpu_exhaustion",
    "metric_name": "cpu_utilization",
    "current_value": 69.2,
    "predicted_breach_value": 95.0,
    "eta_minutes": 6.4,
    "confidence": 97.8,
    "explanation": "cpu_utilization at 69.2% (growing 10.72%/min) will reach 95% in 6.4 minutes (confidence: 98%)",
    "recommended_action": "Scale out horizontally or increase instance size"
  }
}
```

### 3. ServiceNow (via SDF)

**Purpose:** Auto-create incident tickets for high-confidence predictions

**Workflow:**
1. Prediction generated (confidence > 90%)
2. Pushed to SDF
3. SDF triggers ServiceNow webhook
4. Incident created with:
   - Priority: P1/P2 based on ETA
   - Assignment group: On-call team
   - Description: Prediction details

### 4. PagerDuty (via SDF)

**Purpose:** Alert on-call engineers for critical predictions

**Workflow:**
1. Prediction generated (confidence > 95% OR ETA < 5 min)
2. Pushed to SDF
3. SDF triggers PagerDuty event API
4. Page sent to on-call engineer

### 5. Splunk/OpenSearch

**Purpose:** Log aggregation and historical analysis

**Log Format:**

```json
{
  "timestamp": "2026-02-06T23:21:38Z",
  "level": "WARNING",
  "source": "incident-predictor-ml",
  "event": "prediction_generated",
  "prediction": { /* ... */ }
}
```

---

## Monitoring & Observability

### Metrics to Track

1. **Prediction Engine Health**
   - Detection cycle duration (ms)
   - Detection cycles per hour
   - Error rate (%)
   - Memory usage (MB)
   - CPU usage (%)

2. **Prediction Quality**
   - Predictions generated per hour
   - High-confidence predictions (>80%)
   - False positive rate
   - True positive rate (validated incidents)
   - Average ETA accuracy

3. **Integration Health**
   - SDF push success rate
   - Dynatrace API latency
   - API error rate

### Prometheus Metrics Example

```python
from prometheus_client import Counter, Histogram, Gauge

prediction_counter = Counter('predictions_generated_total', 'Total predictions')
confidence_histogram = Histogram('prediction_confidence', 'Prediction confidence scores')
cycle_duration = Histogram('detection_cycle_duration_seconds', 'Cycle duration')
```

### Grafana Dashboard (Sample Queries)

```
# Detection cycles per hour
rate(detection_cycles_total[1h])

# Average prediction confidence
avg(prediction_confidence)

# 95th percentile cycle duration
histogram_quantile(0.95, detection_cycle_duration_seconds)
```

---

## Troubleshooting

### Common Issues

#### Issue 1: No predictions generated

**Symptoms:**
- Detection cycles complete successfully
- No anomalies detected

**Causes:**
- All metrics within normal range (expected)
- Baseline window too short
- Confidence threshold too high

**Solutions:**
```bash
# Lower confidence threshold temporarily
export MIN_CONFIDENCE=70.0

# Increase baseline window
export BASELINE_WINDOW_HOURS=48

# Check mock mode is disabled
export MOCK_MODE=false
```

#### Issue 2: Too many false positives

**Symptoms:**
- Many predictions generated
- Low validation rate

**Causes:**
- Confidence threshold too low
- Noisy metrics
- Insufficient baseline data

**Solutions:**
```bash
# Increase confidence threshold
export MIN_CONFIDENCE=85.0

# Increase baseline window for more stable baseline
export BASELINE_WINDOW_HOURS=72
```

#### Issue 3: High detection cycle latency

**Symptoms:**
- Cycles taking > 2 seconds
- Warnings in logs

**Causes:**
- Too many metrics being processed
- Isolation Forest training on large dataset
- Network latency to Dynatrace API

**Solutions:**
```python
# Reduce metrics being processed
selected_metrics = ["cpu_utilization", "memory_utilization"]

# Use smaller Isolation Forest
anomaly_detector = AnomalyDetector(
    isolation_forest_estimators=50  # default: 100
)
```

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python -m src.main
```

---

## Security Considerations

### 1. Secrets Management

**Never hardcode secrets.** Use environment variables or secret managers.

**Azure Key Vault Integration:**

```bash
# Store secrets
az keyvault secret set \
  --vault-name kv-incident-predictor \
  --name sdf-api-key \
  --value "your-secret-key"

# Retrieve in application
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://kv-incident-predictor.vault.azure.net/", credential=credential)
sdf_api_key = client.get_secret("sdf-api-key").value
```

### 2. Network Security

- Use private endpoints for Dynatrace/SDF communication
- Implement network security groups (NSGs)
- Enable TLS 1.2+ for all API calls

### 3. Least Privilege Access

- Dynatrace token: `metrics.read` only
- SDF token: `events.write` only
- Container runs as non-root user

---

## Rollback Procedures

### Quick Rollback (Docker)

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and deploy
docker-compose up -d --build
```

### Kubernetes Rollback

```bash
# Rollback to previous deployment
kubectl rollout undo deployment/incident-predictor -n monitoring

# Verify rollback
kubectl rollout status deployment/incident-predictor -n monitoring
```

### Disable Prediction Engine

```bash
# Set detection interval to very high value (effectively disabled)
kubectl set env deployment/incident-predictor DETECTION_INTERVAL_SECONDS=86400

# Or scale to 0 replicas
kubectl scale deployment/incident-predictor --replicas=0
```

---

## Support & Contact

For issues, questions, or feature requests:

- **GitHub Issues**: https://github.com/EPdacoder05/incident-replay-tool/issues
- **Documentation**: https://github.com/EPdacoder05/incident-replay-tool
- **Team Email**: devops@quantumhealth.com

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-06  
**Next Review:** 2026-03-06
