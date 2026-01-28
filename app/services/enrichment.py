import httpx
from typing import Optional


class EnrichmentService:
    """Service for enriching alerts with threat intelligence data."""
    
    def __init__(self):
        self.abuseipdb_key: Optional[str] = None
        self.virustotal_key: Optional[str] = None
    
    def configure(self, abuseipdb_key: str = None, virustotal_key: str = None):
        """Configure API keys for threat intelligence services."""
        self.abuseipdb_key = abuseipdb_key
        self.virustotal_key = virustotal_key
    
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
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    params={"ipAddress": ip_address, "maxAgeInDays": 90},
                    headers={
                        "Key": self.abuseipdb_key,
                        "Accept": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    result["data"] = {
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
                    result["error"] = f"API returned status {response.status_code}"
                    
        except Exception as e:
            result["error"] = str(e)
        
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
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/domains/{domain}",
                    headers={"x-apikey": self.virustotal_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json().get("data", {}).get("attributes", {})
                    stats = data.get("last_analysis_stats", {})
                    result["data"] = {
                        "malicious_votes": stats.get("malicious", 0),
                        "suspicious_votes": stats.get("suspicious", 0),
                        "harmless_votes": stats.get("harmless", 0),
                        "reputation": data.get("reputation"),
                        "registrar": data.get("registrar"),
                        "creation_date": data.get("creation_date")
                    }
                else:
                    result["error"] = f"API returned status {response.status_code}"
                    
        except Exception as e:
            result["error"] = str(e)
        
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