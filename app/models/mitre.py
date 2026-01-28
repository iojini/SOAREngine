from typing import List, Optional
from pydantic import BaseModel, Field


class MitreTechnique(BaseModel):
    """A MITRE ATT&CK technique."""
    technique_id: str = Field(..., description="ATT&CK technique ID (e.g., T1566)")
    name: str = Field(..., description="Technique name")
    tactic: str = Field(..., description="ATT&CK tactic (e.g., Initial Access)")
    description: Optional[str] = Field(None, description="Brief description")
    url: str = Field(..., description="Link to MITRE ATT&CK page")


class AlertMitreMapping(BaseModel):
    """Mapping of an alert to MITRE ATT&CK techniques."""
    alert_id: str
    techniques: List[MitreTechnique]
    confidence: str = Field(..., description="Confidence level: low, medium, high")


# Common MITRE ATT&CK techniques for security alerts
MITRE_TECHNIQUES = {
    "T1566": MitreTechnique(
        technique_id="T1566",
        name="Phishing",
        tactic="Initial Access",
        description="Adversaries may send phishing messages to gain access to victim systems.",
        url="https://attack.mitre.org/techniques/T1566/"
    ),
    "T1566.001": MitreTechnique(
        technique_id="T1566.001",
        name="Spearphishing Attachment",
        tactic="Initial Access",
        description="Adversaries may send spearphishing emails with a malicious attachment.",
        url="https://attack.mitre.org/techniques/T1566/001/"
    ),
    "T1566.002": MitreTechnique(
        technique_id="T1566.002",
        name="Spearphishing Link",
        tactic="Initial Access",
        description="Adversaries may send spearphishing emails with a malicious link.",
        url="https://attack.mitre.org/techniques/T1566/002/"
    ),
    "T1190": MitreTechnique(
        technique_id="T1190",
        name="Exploit Public-Facing Application",
        tactic="Initial Access",
        description="Adversaries may attempt to exploit a weakness in an Internet-facing host.",
        url="https://attack.mitre.org/techniques/T1190/"
    ),
    "T1133": MitreTechnique(
        technique_id="T1133",
        name="External Remote Services",
        tactic="Initial Access",
        description="Adversaries may leverage external-facing remote services to initially access a network.",
        url="https://attack.mitre.org/techniques/T1133/"
    ),
    "T1078": MitreTechnique(
        technique_id="T1078",
        name="Valid Accounts",
        tactic="Defense Evasion",
        description="Adversaries may obtain and abuse credentials of existing accounts.",
        url="https://attack.mitre.org/techniques/T1078/"
    ),
    "T1110": MitreTechnique(
        technique_id="T1110",
        name="Brute Force",
        tactic="Credential Access",
        description="Adversaries may use brute force techniques to gain access to accounts.",
        url="https://attack.mitre.org/techniques/T1110/"
    ),
    "T1486": MitreTechnique(
        technique_id="T1486",
        name="Data Encrypted for Impact",
        tactic="Impact",
        description="Adversaries may encrypt data on target systems to interrupt availability.",
        url="https://attack.mitre.org/techniques/T1486/"
    ),
    "T1071": MitreTechnique(
        technique_id="T1071",
        name="Application Layer Protocol",
        tactic="Command and Control",
        description="Adversaries may communicate using application layer protocols.",
        url="https://attack.mitre.org/techniques/T1071/"
    ),
    "T1059": MitreTechnique(
        technique_id="T1059",
        name="Command and Scripting Interpreter",
        tactic="Execution",
        description="Adversaries may abuse command and script interpreters to execute commands.",
        url="https://attack.mitre.org/techniques/T1059/"
    ),
    "T1059.001": MitreTechnique(
        technique_id="T1059.001",
        name="PowerShell",
        tactic="Execution",
        description="Adversaries may abuse PowerShell commands and scripts for execution.",
        url="https://attack.mitre.org/techniques/T1059/001/"
    ),
    "T1055": MitreTechnique(
        technique_id="T1055",
        name="Process Injection",
        tactic="Defense Evasion",
        description="Adversaries may inject code into processes to evade defenses.",
        url="https://attack.mitre.org/techniques/T1055/"
    ),
    "T1021": MitreTechnique(
        technique_id="T1021",
        name="Remote Services",
        tactic="Lateral Movement",
        description="Adversaries may use remote services to move laterally.",
        url="https://attack.mitre.org/techniques/T1021/"
    ),
    "T1048": MitreTechnique(
        technique_id="T1048",
        name="Exfiltration Over Alternative Protocol",
        tactic="Exfiltration",
        description="Adversaries may steal data by exfiltrating it over a different protocol.",
        url="https://attack.mitre.org/techniques/T1048/"
    ),
    "T1105": MitreTechnique(
        technique_id="T1105",
        name="Ingress Tool Transfer",
        tactic="Command and Control",
        description="Adversaries may transfer tools from an external system into a compromised environment.",
        url="https://attack.mitre.org/techniques/T1105/"
    ),
}


# Keyword mappings to identify likely techniques
KEYWORD_TECHNIQUE_MAP = {
    # Phishing related
    "phishing": ["T1566", "T1566.001", "T1566.002"],
    "spearphishing": ["T1566.001", "T1566.002"],
    "malicious email": ["T1566", "T1566.001"],
    "suspicious attachment": ["T1566.001"],
    "suspicious link": ["T1566.002"],
    
    # Authentication related
    "brute force": ["T1110"],
    "failed login": ["T1110", "T1078"],
    "suspicious login": ["T1078", "T1133"],
    "unauthorized access": ["T1078"],
    "credential": ["T1078", "T1110"],
    
    # Malware related
    "ransomware": ["T1486", "T1059"],
    "malware": ["T1059", "T1055", "T1105"],
    "trojan": ["T1059", "T1055"],
    "virus": ["T1059", "T1055"],
    "encryption": ["T1486"],
    
    # Command and control
    "c2": ["T1071", "T1105"],
    "command and control": ["T1071", "T1105"],
    "callback": ["T1071"],
    "beacon": ["T1071"],
    
    # Execution
    "powershell": ["T1059.001"],
    "script": ["T1059"],
    "execution": ["T1059"],
    
    # Lateral movement
    "lateral movement": ["T1021"],
    "remote desktop": ["T1021"],
    "rdp": ["T1021"],
    
    # Network related
    "exploit": ["T1190"],
    "vulnerability": ["T1190"],
    "exfiltration": ["T1048"],
    "data theft": ["T1048"],
}