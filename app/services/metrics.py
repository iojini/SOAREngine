from prometheus_client import Counter, Histogram, Gauge

# Alert metrics
ALERTS_CREATED = Counter(
    "soarengine_alerts_created_total",
    "Total number of alerts created",
    ["severity", "source"]
)

ALERTS_ENRICHED = Counter(
    "soarengine_alerts_enriched_total",
    "Total number of alerts enriched"
)

ALERTS_BY_STATUS = Gauge(
    "soarengine_alerts_by_status",
    "Current number of alerts by status",
    ["status"]
)

# Playbook metrics
PLAYBOOKS_EXECUTED = Counter(
    "soarengine_playbooks_executed_total",
    "Total number of playbook executions",
    ["playbook_name", "success"]
)

PLAYBOOK_EXECUTION_TIME = Histogram(
    "soarengine_playbook_execution_seconds",
    "Time spent executing playbooks",
    ["playbook_name"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Enrichment metrics
ENRICHMENT_REQUESTS = Counter(
    "soarengine_enrichment_requests_total",
    "Total number of enrichment requests",
    ["enrichment_type", "source"]
)

ENRICHMENT_LATENCY = Histogram(
    "soarengine_enrichment_latency_seconds",
    "Latency of enrichment requests",
    ["enrichment_type"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

# MITRE mapping metrics
MITRE_MAPPINGS = Counter(
    "soarengine_mitre_mappings_total",
    "Total number of MITRE ATT&CK mappings performed"
)

MITRE_TECHNIQUES_MATCHED = Counter(
    "soarengine_mitre_techniques_matched_total",
    "Total number of MITRE techniques matched",
    ["technique_id", "tactic"]
)