# SOAREngine

A Security Orchestration, Automation & Response (SOAR) platform built with Python/FastAPI and C#/.NET Core.

![CI](https://github.com/iojini/SOAREngine/actions/workflows/ci.yml/badge.svg)

## Overview

SOAREngine automates security operations by:
- **Ingesting security alerts** from multiple sources (SIEM, EDR, Firewall, IDS, Webhooks)
- **Enriching alerts** with threat intelligence from AbuseIPDB and VirusTotal
- **Mapping alerts to MITRE ATT&CK** techniques automatically
- **Executing automated playbooks** based on configurable trigger conditions
- **Sending notifications** via Slack webhooks
- **Providing analytics** with dashboard-ready statistics endpoints
- **Exposing Prometheus metrics** for production monitoring

## Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  External       │     │   .NET Core     │     │                 │
│  Systems        │────▶│   Webhook       │────▶│   FastAPI       │
│  (SIEM/EDR)     │     │   Receiver      │     │   REST API      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌──────────────────────────┼──────────────────────────┐
                              │                          │                          │
                              ▼                          ▼                          ▼
                    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
                    │   SQLite        │      │   Playbook      │      │   Enrichment    │
                    │   Database      │      │   Engine        │      │   Service       │
                    └─────────────────┘      └────────┬────────┘      └─────────────────┘
                                                      │
                         ┌───────────┬────────────────┼────────────┬───────────┐
                         ▼           ▼                ▼            ▼           ▼
                    ┌─────────┐ ┌─────────┐    ┌─────────┐  ┌─────────┐ ┌─────────┐
                    │  MITRE  │ │  Slack  │    │ Threat  │  │ Ticket  │ │ Metrics │
                    │ Mapping │ │ Notify  │    │  Intel  │  │ Create  │ │ Export  │
                    └─────────┘ └─────────┘    └─────────┘  └─────────┘ └─────────┘
```

## Features

### Core Platform (Python/FastAPI)
- **Alert Management**: Create, track, and manage security alerts with severity levels and status tracking
- **Threat Intelligence Enrichment**: Automatic IP and domain reputation lookups via AbuseIPDB and VirusTotal
- **MITRE ATT&CK Mapping**: Automatically map alerts to ATT&CK techniques and tactics
- **Playbook Engine**: Define automated response workflows with triggers and actions
- **Slack Notifications**: Send formatted alerts to Slack channels
- **Statistics API**: Dashboard-ready endpoints for analytics and reporting
- **Prometheus Metrics**: Production-ready metrics for monitoring

### Webhook Receiver (C#/.NET Core)
- **External Integration**: Receive webhooks from SIEM, EDR, and other security tools
- **Alert Forwarding**: Automatically forward alerts to SOAREngine API
- **Generic Webhook Support**: Handle arbitrary JSON payloads

### Security & Production Features
- **API Key Authentication**: Secure all endpoints with API key validation
- **Rate Limiting**: Protect against API abuse (30 requests/minute)
- **Environment Configuration**: Manage settings via environment variables
- **Docker Support**: Containerized deployment ready
- **CI/CD Pipeline**: Automated testing and builds with GitHub Actions

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend API** | Python 3.12, FastAPI, Pydantic |
| **Database** | SQLite with SQLAlchemy (async) |
| **Webhook Receiver** | C# / .NET 8.0 |
| **HTTP Client** | httpx (async) |
| **Metrics** | Prometheus |
| **Rate Limiting** | SlowAPI |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker |

## Quick Start

### Prerequisites
- Python 3.10+
- .NET 8.0 SDK (for webhook receiver)
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

### Run Webhook Receiver (Optional)
```bash
cd webhook-receiver/WebhookReceiver
dotnet run
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
- **Webhook Receiver**: http://localhost:5279/swagger

## API Endpoints

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/alerts/` | Create a new alert (rate limited) |
| GET | `/alerts/` | List all alerts |
| GET | `/alerts/{id}` | Get alert by ID |
| PATCH | `/alerts/{id}/status` | Update alert status |
| POST | `/alerts/{id}/enrich` | Enrich alert with threat intel |
| POST | `/alerts/{id}/run-playbooks` | Execute matching playbooks |
| DELETE | `/alerts/{id}` | Delete an alert |

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

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/notifications/slack` | Send Slack notification |
| POST | `/notifications/alerts/{id}/notify` | Notify about specific alert |

### Statistics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/statistics/alerts` | Get alert statistics |
| GET | `/statistics/dashboard` | Get dashboard stats |
| GET | `/statistics/top-source-ips` | Get top source IPs |

### Webhook Receiver (.NET)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/Webhook/alert` | Receive and forward alert |
| POST | `/api/Webhook/generic` | Receive generic webhook |
| GET | `/api/Webhook/health` | Health check |

### Monitoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/config` | View configuration |
| GET | `/metrics` | Prometheus metrics |

## Authentication

All API endpoints (except `/health` and `/metrics`) require an API key.

**Include the header:**
```
X-API-Key: your-api-key
```

**Configure API keys in `.env`:**
```bash
API_KEYS=your-secret-key-1,your-secret-key-2
```

## Configuration

Copy `.env.example` to `.env` and configure:
```bash
# Application Settings
APP_NAME=SOAREngine
DEBUG=false

# API Keys for authentication
API_KEYS=your-secret-key

# Threat Intelligence APIs
ABUSEIPDB_API_KEY=your-key
VIRUSTOTAL_API_KEY=your-key

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
SLACK_DEFAULT_CHANNEL=#security-alerts

# Playbook Settings
PLAYBOOK_AUTO_RUN=true

# Metrics
METRICS_ENABLED=true
```

## Built-in Playbooks

1. **High Severity Auto-Enrich**: Automatically enriches high/critical alerts and notifies Slack
2. **EDR Alert Response**: Handles EDR alerts with enrichment and ticket creation
3. **Malware Investigation**: Triggered by malware keywords, recommends host isolation

## Prometheus Metrics

SOAREngine exposes custom metrics:

| Metric | Description |
|--------|-------------|
| `soarengine_alerts_created_total` | Total alerts created (by severity, source) |
| `soarengine_alerts_enriched_total` | Total alerts enriched |
| `soarengine_playbooks_executed_total` | Playbook executions (by name, success) |
| `soarengine_mitre_mappings_total` | MITRE ATT&CK mappings performed |

## Project Structure
```
SOAREngine/
├── .github/workflows/
│   └── ci.yml              # GitHub Actions CI/CD
├── app/
│   ├── api/
│   │   ├── alerts.py       # Alert endpoints
│   │   ├── playbooks.py    # Playbook endpoints
│   │   ├── mitre.py        # MITRE ATT&CK endpoints
│   │   ├── notifications.py # Notification endpoints
│   │   └── statistics.py   # Statistics endpoints
│   ├── auth/
│   │   └── api_key.py      # API key authentication
│   ├── database/
│   │   ├── db.py           # Database configuration
│   │   ├── models.py       # SQLAlchemy models
│   │   └── repository.py   # Data access layer
│   ├── models/
│   │   ├── alert.py        # Alert data models
│   │   ├── playbook.py     # Playbook data models
│   │   └── mitre.py        # MITRE ATT&CK models
│   ├── services/
│   │   ├── enrichment.py   # Threat intel enrichment
│   │   ├── playbook_engine.py  # Playbook execution
│   │   ├── mitre_mapper.py # MITRE ATT&CK mapping
│   │   ├── notifications.py # Slack notifications
│   │   └── metrics.py      # Prometheus metrics
│   ├── config.py           # Configuration management
│   └── rate_limit.py       # Rate limiting
├── webhook-receiver/       # .NET Core webhook service
│   └── WebhookReceiver/
│       ├── Controllers/
│       │   └── WebhookController.cs
│       ├── Models/
│       │   └── AlertPayload.cs
│       ├── Services/
│       │   └── SoarEngineService.cs
│       └── Program.cs
├── tests/
│   └── test_api.py         # API tests
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
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
- [ ] PostgreSQL database support
- [ ] Real-time WebSocket updates
- [ ] Alert correlation engine
- [ ] Additional threat intel feeds
- [ ] Kubernetes deployment manifests
- [ ] Multi-tenancy support

## License

MIT License