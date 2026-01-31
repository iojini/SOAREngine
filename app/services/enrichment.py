import httpx
import logging
from typing import Optional

from app.config import get_settings
from app.services.reliability import (
    dead_letter_queue,
    enrichment_circuit,
    with_retry,
    OperationType,
)

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Service for enriching alerts with threat intelligence data."""
    
    def __init__(self):
        settings = get_settings()
        self.abuseipdb_key: Optional[str] = settings.abuseipdb_api_key
        self.virustotal_key: Optional[str] = settings.virustotal_api_key
        self.timeout: int = settings.enrichment_timeout
    
    def configure(self, abuseipdb_key: str = None, virustotal_key: str = None):
        """Configure API keys for threat intelligence services."""
        self.abuseipdb_key = abuseipdb_key
        self.virustotal_key = virustotal_key
    
    @with_retry(max_attempts=3, min_wait=1, max_wait=10, exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def _call_abuseipdb(self, ip_address: str) -> dict:
        """Call AbuseIPDB API with retry logic."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.abuseipdb.com/api/v2/check",
                params={"ipAddress": ip_address, "maxAgeInDays": 90},
                headers={
                    "Key": self.abuseipdb_key,
                    "Accept": "application/json"
                },
                timeout=float(self.timeout)
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {})
                return {
                    "is_public": data.get("isPublic"),
                    "abuse_confidence_score": data.get("abuseConfidenceScore"),
                    "country_code": data.get("countryCode"),
                    "isp": data.get("isp"),
                    "domain": data.get("domain"),
                    "total_reports": data.get("totalReports"),
                    "is_tor": data.get("isTor"),
                    "is_whitelisted": data.get("isWhitelisted")
                }
            else:
                raise httpx.HTTPError(f"API returned status {response.status_code}")

    @with_retry(max_attempts=3, min_wait=1, max_wait=10, exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def _call_virustotal(self, domain: str) -> dict:
        """Call VirusTotal API with retry logic."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.virustotal.com/api/v3/domains/{domain}",
                headers={"x-apikey": self.virustotal_key},
                timeout=float(self.timeout)
            )
            
            if response.status_code == 200:
                data = response.json().get("data", {}).get("attributes", {})
                stats = data.get("last_analysis_stats", {})
                return {
                    "malicious_votes": stats.get("malicious", 0),
                    "suspicious_votes": stats.get("suspicious", 0),
                    "harmless_votes": stats.get("harmless", 0),
                    "reputation": data.get("reputation"),
                    "registrar": data.get("registrar"),
                    "creation_date": data.get("creation_date")
                }
            else:
                raise httpx.HTTPError(f"API returned status {response.status_code}")

    async def enrich_ip(self, ip_address: str) -> dict:
        """Enrich an IP address with threat intelligence."""
        result = {
            "ip": ip_address,
            "source": "abuseipdb",
            "data": None,
            "error": None
        }
        
        if not self.abuseipdb_key:
            result["data"] = self._mock_ip_data(ip_address)
            result["source"] = "mock"
            return result
        
        # Check circuit breaker
        if not await enrichment_circuit.can_execute():
            logger.warning(f"Circuit breaker OPEN for enrichment. Using mock data for {ip_address}")
            await dead_letter_queue.add(
                operation_type=OperationType.ENRICHMENT,
                payload={"ip_address": ip_address},
                error="Circuit breaker open",
                alert_id=None
            )
            result["data"] = self._mock_ip_data(ip_address)
            result["source"] = "mock (circuit open)"
            return result
        
        try:
            data = await self._call_abuseipdb(ip_address)
            result["data"] = data
            await enrichment_circuit.record_success()
            logger.info(f"Successfully enriched IP {ip_address}")
        except Exception as e:
            await enrichment_circuit.record_failure()
            await dead_letter_queue.add(
                operation_type=OperationType.ENRICHMENT,
                payload={"ip_address": ip_address},
                error=str(e),
                alert_id=None
            )
            result["error"] = str(e)
            result["data"] = self._mock_ip_data(ip_address)
            result["source"] = "mock (fallback)"
            logger.error(f"Failed to enrich IP {ip_address}: {e}")
                
        return result
    
    async def enrich_domain(self, domain: str) -> dict:
        """Enrich a domain with threat intelligence."""
        result = {
            "domain": domain,
            "source": "virustotal",
            "data": None,
            "error": None
        }
        
        if not self.virustotal_key:
            result["data"] = self._mock_domain_data(domain)
            result["source"] = "mock"
            return result
        
        # Check circuit breaker
        if not await enrichment_circuit.can_execute():
            logger.warning(f"Circuit breaker OPEN for enrichment. Using mock data for {domain}")
            await dead_letter_queue.add(
                operation_type=OperationType.ENRICHMENT,
                payload={"domain": domain},
                error="Circuit breaker open",
                alert_id=None
            )
            result["data"] = self._mock_domain_data(domain)
            result["source"] = "mock (circuit open)"
            return result
        
        try:
            data = await self._call_virustotal(domain)
            result["data"] = data
            await enrichment_circuit.record_success()
            logger.info(f"Successfully enriched domain {domain}")
        except Exception as e:
            await enrichment_circuit.record_failure()
            await dead_letter_queue.add(
                operation_type=OperationType.ENRICHMENT,
                payload={"domain": domain},
                error=str(e),
                alert_id=None
            )
            result["error"] = str(e)
            result["data"] = self._mock_domain_data(domain)
            result["source"] = "mock (fallback)"
            logger.error(f"Failed to enrich domain {domain}: {e}")
                
        return result
    
    async def enrich_alert(self, alert) -> dict:
        """Enrich an alert with all available threat intelligence."""
        enrichment = {}
        
        if alert.source_ip:
            enrichment["source_ip"] = await self.enrich_ip(alert.source_ip)
        
        if alert.destination_ip:
            enrichment["destination_ip"] = await self.enrich_ip(alert.destination_ip)
        
        if alert.domain:
            enrichment["domain"] = await self.enrich_domain(alert.domain)
        
        return enrichment
    
    def _mock_ip_data(self, ip: str) -> dict:
        """Return mock IP data for testing without API keys."""
        return {
            "is_public": True,
            "abuse_confidence_score": 75,
            "country_code": "RU",
            "isp": "Mock ISP Provider",
            "domain": "mock-domain.com",
            "total_reports": 42,
            "is_tor": False,
            "is_whitelisted": False,
            "note": "Mock data - configure API key for real results"
        }
    
    def _mock_domain_data(self, domain: str) -> dict:
        """Return mock domain data for testing without API keys."""
        return {
            "malicious_votes": 3,
            "suspicious_votes": 2,
            "harmless_votes": 65,
            "reputation": -5,
            "registrar": "Mock Registrar Inc.",
            "creation_date": "2020-01-15",
            "note": "Mock data - configure API key for real results"
        }


# Global instance
enrichment_service = EnrichmentService()