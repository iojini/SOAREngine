# SOAREngine

A Security Orchestration, Automation & Response (SOAR) platform built with Python and FastAPI.

## Overview

SOAREngine automates security operations by:
- **Ingesting security alerts** from multiple sources (SIEM, EDR, Firewall, IDS)
- **Enriching alerts** with threat intelligence from AbuseIPDB and VirusTotal
- **Executing automated playbooks** based on configurable trigger conditions
- **Orchestrating responses** including notifications, ticket creation, and host isolation

## Features

- **Alert Management**: Create, track, and manage security alerts with severity levels and status tracking
- **Threat Intelligence Enrichment**: Automatic IP and domain reputation lookups
- **Playbook Engine**: Define automated response workflows with YAML-style triggers and actions
- **REST API**: Full-featured API with OpenAPI/Swagger documentation
- **Extensible Architecture**: Easy to add new enrichment sources and response actions

## Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Alert Sources  │────▶│   FastAPI       │────▶│  Alert Store    │
│  (SIEM/EDR)     │     │   REST API      │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Playbook Engine      │
                    │  ┌──────────────────┐   │
                    │  │ Trigger Matching │   │
                    │  └────────┬─────────┘   │
                    │  ┌────────▼─────────┐   │
                    │  │ Action Executor  │   │
                    │  └──────────────────┘   │
                    └────────────┬────────────┘
                                 │
        ┌───────────┬────────────┼────────────┬───────────┐
        ▼           ▼            ▼            ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Enrich  │ │  Slack  │ │ Tickets │ │ Block   │ │ Isolate │
   │ Service │ │ Notify  │ │ Create  │ │ IP      │ │ Host    │
   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/SOAREngine.git
cd SOAREngine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

### Access the API
- **Swagger UI**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## API Endpoints

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/alerts/` | Create a new alert |
| GET | `/alerts/` | List all alerts |
| GET | `/alerts/{id}` | Get alert by ID |
| PATCH | `/alerts/{id}/status` | Update alert status |
| POST | `/alerts/{id}/enrich` | Enrich alert with threat intel |
| POST | `/alerts/{id}/run-playbooks` | Execute matching playbooks |

### Playbooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/playbooks/` | Create a new playbook |
| GET | `/playbooks/` | List all playbooks |
| GET | `/playbooks/{id}` | Get playbook by ID |
| DELETE | `/playbooks/{id}` | Delete a playbook |

## Example Usage

### Create an Alert
```bash
curl -X POST "http://127.0.0.1:8000/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Suspicious login attempt",
    "description": "Multiple failed logins from external IP",
    "severity": "high",
    "source": "siem",
    "source_ip": "185.220.101.42"
  }'
```

### Run Playbooks
```bash
curl -X POST "http://127.0.0.1:8000/alerts/{alert_id}/run-playbooks"
```

## Built-in Playbooks

1. **High Severity Auto-Enrich**: Automatically enriches high/critical alerts and notifies Slack
2. **EDR Alert Response**: Handles EDR alerts with enrichment and ticket creation
3. **Malware Investigation**: Triggered by malware keywords, recommends host isolation

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.12
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic
- **API Docs**: OpenAPI/Swagger (auto-generated)

## Project Structure
```
SOAREngine/
├── app/
│   ├── api/
│   │   ├── alerts.py       # Alert endpoints
│   │   └── playbooks.py    # Playbook endpoints
│   ├── models/
│   │   ├── alert.py        # Alert data models
│   │   └── playbook.py     # Playbook data models
│   └── services/
│       ├── enrichment.py   # Threat intel enrichment
│       └── playbook_engine.py  # Playbook execution
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
└── README.md
```

## Future Enhancements

- [ ] Redis queue for async alert processing
- [ ] PostgreSQL database for persistence
- [ ] Real Slack/Teams webhook integration
- [ ] MITRE ATT&CK mapping
- [ ] Kubernetes deployment manifests
- [ ] Prometheus metrics endpoint
- [ ] Authentication/API keys

## License

MIT License