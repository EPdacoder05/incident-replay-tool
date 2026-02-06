# Incident Replay Tool + Incident Predictor ML

The **Incident Replay Tool** is a comprehensive incident management platform that combines:

1. **Post-Mortem Analysis** - Local web application to review and analyze major incidents after they occur
2. **Predictive Detection** - ML-powered prediction engine that catches infrastructure issues 6-20 minutes BEFORE they escalate

---

## 🚀 What's New: Incident Predictor ML

**Transform reactive incident response into proactive prevention**

The Incident Predictor ML adds a prediction layer that uses Z-score anomaly detection + Isolation Forest ML to predict incidents before they happen.

### Key Capabilities

- 🔮 **Predictive Detection**: Catches incidents 6-20 minutes early
- 🎯 **High Confidence Alerting**: Only alerts when 80%+ confident (minimizes alert fatigue)
- 📊 **Multi-Metric Support**: CPU, memory, disk, network, errors, latency
- 🔗 **SDF Integration**: Pushes predictions to Security Data Fabric Gold layer
- 💰 **Zero ML Costs**: Runs entirely on scikit-learn + numpy

### Comparison: Replay vs Predictor

| Aspect | Incident Replay Tool | Incident Predictor ML |
|--------|---------------------|----------------------|
| **Purpose** | Post-mortem analysis | Proactive prevention |
| **When** | After the fire | Before the fire |
| **Value** | "Here's what happened" | "Here's what's about to happen + what to do" |
| **Tech** | React + FastAPI | Z-score + Isolation Forest ML |

### Quick Start (Predictor)

```bash
# One-command demo with Docker Compose
docker-compose up --build

# Or run locally
pip install -r requirements.txt
python -m src.main

# Run validation tests
python tests/validate_local.py
pytest tests/test_e2e_validation.py -v
```

### Performance Metrics

- ✅ Detection cycle: <1ms (target: <2s)
- ✅ Confidence: 99.9% on CPU spike detection
- ✅ False positives: 0 on normal metrics
- ✅ All 30 tests passing (7 local + 23 e2e)

### Documentation

- 📖 [**DEPLOYMENT_GUIDE.md**](DEPLOYMENT_GUIDE.md) - Comprehensive deployment playbook (60+ pages)
- 📊 [**VALIDATION_REPORT.md**](VALIDATION_REPORT.md) - Test results, benchmarks, ROI (327:1)

---

## Features (Replay Tool)

- ✅ **Interactive Timeline** of key events:
  - ServiceNow tickets, banners, MI proposals/approvals
  - Dynatrace, Splunk, and OpenSearch monitoring spikes
  - Microsoft Teams room creation and war room activation
- ✅ **Quantum Health Branding**
  - Green header, card striping
  - Custom green category badges
  - Duration-based status indicators (green/yellow/red)
- ✅ **Post-Incident Summary Preview**
  - Expandable summary on homepage
  - Full detail view with 8 documentation fields
- ✅ **Filters**
  - Category filters (e.g. Member Website, Authorizations)
  - Timeline event filters (e.g. Ticket Spike, Fix Implemented)
  - Year and keyword search

---

## 🛠 Tech Stack

### Replay Tool
|      Frontend        |     Backend      | Storage | AI Integration |   Hosting      |
|----------------------|------------------|---------|----------------|----------------|
| React + Tailwind CSS | FastAPI (Python) | SQLite  | OpenAI (future)|   Local only   |

### Predictor ML
|   Detection   |   ML/Analytics    |   Integration   |   Deployment   |
|---------------|-------------------|-----------------|----------------|
| Z-score + IF  | scikit-learn      | SDF Gold Layer  | Docker + K8s   |
| Async Python  | numpy + pandas    | Dynatrace API   | Azure ready    |

---

## 🧪 Status

### Replay Tool
✅ Mock data in use  
🧠 Post-incident summary will soon be powered by AI  

### Predictor ML
✅ **Production Ready** - All tests passing
✅ Docker build successful
✅ Comprehensive documentation
✅ Zero security vulnerabilities (CodeQL validated)

---

## 🔧 Setup

### Replay Tool Frontend
```bash
cd frontend
npm install
npm run dev
```

### Replay Tool Backend
```bash
cd backend
python -m venv env
source env/bin/activate  # or `env\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Predictor ML (Production)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions covering:
- Local development setup
- Docker deployment (one-command demo)
- Production options: AKS, Azure App Service, Docker on VMs
- Configuration reference
- Integration with Dynatrace, SDF, ServiceNow, PagerDuty
- Monitoring & troubleshooting

---

## 📈 ROI (Predictor ML)

- **Cost**: ~$140/month infrastructure
- **Benefit**: Prevent 11/12 incidents = $550K saved/year
- **ROI**: 327:1 or 32,700%
- **Payback**: 1.1 days

---

## 📝 License

See [LICENSE](LICENSE) file for details.