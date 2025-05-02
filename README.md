# Incident Replay Tool

The **Incident Replay Tool** is a local web application built to help Quantum Health management review and analyze major incidents (MIs) after they occur. It offers a clear, filterable timeline of incident events across systems, and auto-generates post-incident documentation.

---

## Features

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

|      Frontend        |     Backend      | Storage | AI Integration |   Hosting      |
|----------------------|------------------|---------|----------------|----------------|
| React + Tailwind CSS | FastAPI (Python) | SQLite  | OpenAI (future)|   Local only   |

---

## 🧪 Status

✅ Mock data in use  
🧠 Post-incident summary will soon be powered by AI  

---

## 🔧 Setup

### Frontend
```bash
cd frontend
npm install
npm run dev

### Backend

cd backend
python -m venv env
source env/bin/activate  # or `env\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload

