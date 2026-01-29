from fastapi.testclient import TestClient

from main import app
from app.auth.api_key import verify_api_key

# Override authentication for tests
async def mock_verify_api_key():
    return "test-key"

app.dependency_overrides[verify_api_key] = mock_verify_api_key

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SOAREngine"


class TestAlertsAPI:
    """Tests for the alerts API endpoints."""

    def test_create_alert(self):
        alert_data = {
            "title": "Test Alert",
            "description": "This is a test alert",
            "severity": "high",
            "source": "siem",
            "source_ip": "192.168.1.1"
        }
        response = client.post("/alerts/", json=alert_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Alert"
        assert data["severity"] == "high"
        assert data["status"] == "pending"
        assert data["id"] is not None

    def test_create_alert_with_minimal_data(self):
        alert_data = {
            "title": "Minimal Alert",
            "severity": "low",
            "source": "firewall"
        }
        response = client.post("/alerts/", json=alert_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Alert"

    def test_create_alert_invalid_severity(self):
        alert_data = {
            "title": "Bad Alert",
            "severity": "super-critical",
            "source": "siem"
        }
        response = client.post("/alerts/", json=alert_data)
        assert response.status_code == 422

    def test_list_alerts(self):
        response = client.get("/alerts/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_alert_by_id(self):
        # First create an alert
        alert_data = {
            "title": "Retrieve Test",
            "severity": "medium",
            "source": "edr"
        }
        create_response = client.post("/alerts/", json=alert_data)
        alert_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/alerts/{alert_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Retrieve Test"

    def test_get_alert_not_found(self):
        response = client.get("/alerts/nonexistent-id")
        assert response.status_code == 404

    def test_update_alert_status(self):
        # Create an alert
        alert_data = {
            "title": "Status Test",
            "severity": "low",
            "source": "ids"
        }
        create_response = client.post("/alerts/", json=alert_data)
        alert_id = create_response.json()["id"]

        # Update status
        response = client.patch(
            f"/alerts/{alert_id}/status",
            params={"status": "processing"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "processing"

    def test_delete_alert(self):
        # Create an alert
        alert_data = {
            "title": "Delete Test",
            "severity": "low",
            "source": "siem"
        }
        create_response = client.post("/alerts/", json=alert_data)
        alert_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/alerts/{alert_id}")
        assert response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/alerts/{alert_id}")
        assert get_response.status_code == 404


class TestPlaybooksAPI:
    """Tests for the playbooks API endpoints."""

    def test_list_playbooks(self):
        response = client.get("/playbooks/")
        assert response.status_code == 200
        playbooks = response.json()
        assert isinstance(playbooks, list)
        assert len(playbooks) >= 3

    def test_get_playbook_by_id(self):
        list_response = client.get("/playbooks/")
        playbook_id = list_response.json()[0]["id"]

        response = client.get(f"/playbooks/{playbook_id}")
        assert response.status_code == 200
        assert response.json()["id"] == playbook_id

    def test_get_playbook_not_found(self):
        response = client.get("/playbooks/nonexistent-id")
        assert response.status_code == 404

    def test_create_playbook(self):
        playbook_data = {
            "name": "Test Playbook",
            "description": "A test playbook",
            "enabled": True,
            "trigger": {
                "min_severity": "high"
            },
            "actions": [
                {"type": "enrich_all"}
            ]
        }
        response = client.post("/playbooks/", json=playbook_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Playbook"
        assert data["id"] is not None

    def test_delete_playbook(self):
        playbook_data = {
            "name": "To Delete",
            "description": "Will be deleted",
            "enabled": True,
            "trigger": {"min_severity": "low"},
            "actions": [{"type": "enrich_all"}]
        }
        create_response = client.post("/playbooks/", json=playbook_data)
        playbook_id = create_response.json()["id"]

        response = client.delete(f"/playbooks/{playbook_id}")
        assert response.status_code == 200

        get_response = client.get(f"/playbooks/{playbook_id}")
        assert get_response.status_code == 404


class TestEnrichment:
    """Tests for alert enrichment functionality."""

    def test_enrich_alert(self):
        alert_data = {
            "title": "Enrichment Test",
            "severity": "high",
            "source": "siem",
            "source_ip": "8.8.8.8",
            "domain": "example.com"
        }
        create_response = client.post("/alerts/", json=alert_data)
        alert_id = create_response.json()["id"]

        response = client.post(f"/alerts/{alert_id}/enrich")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enriched"
        assert data["enrichment_data"] is not None


class TestMitreAPI:
    """Tests for MITRE ATT&CK API."""

    def test_list_techniques(self):
        response = client.get("/mitre/techniques")
        assert response.status_code == 200
        techniques = response.json()
        assert isinstance(techniques, list)
        assert len(techniques) > 0

    def test_get_technique(self):
        response = client.get("/mitre/techniques/T1566")
        assert response.status_code == 200
        data = response.json()
        assert data["technique_id"] == "T1566"
        assert data["name"] == "Phishing"

    def test_map_alert_to_mitre(self):
        alert_data = {
            "title": "Ransomware detected",
            "description": "Malware encrypted files",
            "severity": "critical",
            "source": "edr"
        }
        create_response = client.post("/alerts/", json=alert_data)
        alert_id = create_response.json()["id"]

        response = client.post(f"/mitre/alerts/{alert_id}/map")
        assert response.status_code == 200
        data = response.json()
        assert data["alert_id"] == alert_id
        assert len(data["techniques"]) > 0