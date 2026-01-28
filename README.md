# SOAREngine

A Security Orchestration, Automation & Response (SOAR) platform built with Python and FastAPI.

![CI](https://github.com/iojini/SOAREngine/actions/workflows/ci.yml/badge.svg)

## Overview

SOAREngine automates security operations by:
- **Ingesting security alerts** from multiple sources (SIEM, EDR, Firewall, IDS)
- **Enriching alerts** with threat intelligence from AbuseIPDB and VirusTotal
- **Mapping alerts to MITRE ATT&CK** techniques automatically
- **Executing automated playbooks** based on configurable trigger conditions
- **Orchestrating responses** including notifications, ticket creation, and host isolation
- **Exposing Prometheus metrics** for production monitoring

## Features

- **Alert Management**: Create, track, and manage security alerts with severity levels and status tracking
- **Threat Intelligence Enrichment**: Automatic IP and domain reputation lookups
- **MITRE ATT&CK Mapping**: Automatically map alerts to ATT&CK techniques and tactics
- **Playbook Engine**: Define automated response workflows with YAML-style triggers and actions
- **Prometheus Metrics**: Production-ready metrics for monitoring alert volumes, enrichment latency, and playbook execution
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
   │ Enrich  │ │  MITRE  │ │  Slack  │ │ Tickets │ │ Metrics │
   │ Service │ │ Mapper  │ │ Notify  │ │ Create  │ │ Export  │
   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
# Clone the repository
git clone https://github.com/iojini/SOAREngine.git
cd SOAREngine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

### Docker
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Access the API
- **Swagger UI**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Prometheus Metrics**: http://127.0.0.1:8000/metrics

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

### MITRE ATT&CK
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mitre/techniques` | List all techniques |
| GET | `/mitre/techniques/{id}` | Get technique by ID |
| GET | `/mitre/tactics/{tactic}/techniques` | Get techniques by tactic |
| POST | `/mitre/alerts/{id}/map` | Map alert to ATT&CK |

### Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

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

### Map Alert to MITRE ATT&CK
```bash
curl -X POST "http://127.0.0.1:8000/mitre/alerts/{alert_id}/map"
```

### Run Playbooks
```bash
curl -X POST "http://127.0.0.1:8000/alerts/{alert_id}/run-playbooks"
```

## Built-in Playbooks

1. **High Severity Auto-Enrich**: Automatically enriches high/critical alerts and notifies Slack
2. **EDR Alert Response**: Handles EDR alerts with enrichment and ticket creation
3. **Malware Investigation**: Triggered by malware keywords, recommends host isolation

## Prometheus Metrics

SOAREngine exposes custom metrics for monitoring:

| Metric | Description |
|--------|-------------|
| `soarengine_alerts_created_total` | Total alerts created (by severity, source) |
| `soarengine_alerts_enriched_total` | Total alerts enriched |
| `soarengine_playbooks_executed_total` | Playbook executions (by name, success) |
| `soarengine_mitre_mappings_total` | MITRE ATT&CK mappings performed |

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.12
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic
- **Metrics**: Prometheus
- **API Docs**: OpenAPI/Swagger (auto-generated)
- **CI/CD**: GitHub Actions
- **Containerization**: Docker

## Project Structure
```
SOAREngine/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── app/
│   ├── api/
│   │   ├── alerts.py       # Alert endpoints
│   │   ├── playbooks.py    # Playbook endpoints
│   │   └── mitre.py        # MITRE ATT&CK endpoints
│   ├── models/
│   │   ├── alert.py        # Alert data models
│   │   ├── playbook.py     # Playbook data models
│   │   └── mitre.py        # MITRE ATT&CK models
│   └── services/
│       ├── enrichment.py   # Threat intel enrichment
│       ├── playbook_engine.py  # Playbook execution
│       ├── mitre_mapper.py # MITRE ATT&CK mapping
│       └── metrics.py      # Prometheus metrics
├── tests/
│   └── test_api.py         # API tests
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── Dockerfile              # Container image
├── docker-compose.yml      # Container orchestration
└── README.md
```

## Running Tests
```bash
pytest tests/ -v
```

## Future Enhancements

- [ ] Redis queue for async alert processing
- [ ] PostgreSQL database for persistence
- [ ] Real Slack/Teams webhook integration
- [ ] Kubernetes deployment manifests
- [ ] Authentication/API keys
- [ ] Alert correlation engine
- [ ] Threat intelligence feed integration

## License

MIT License