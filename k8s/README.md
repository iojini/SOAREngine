# SOAREngine Kubernetes Deployment

This directory contains Kubernetes manifests for deploying SOAREngine to a Kubernetes cluster.

## Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Namespace: soarengine                     ││
│  │                                                              ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         ││
│  │  │   API       │  │  Webhook    │  │  Dashboard  │         ││
│  │  │  (3 pods)   │  │  (2 pods)   │  │  (2 pods)   │         ││
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         ││
│  │         │                │                │                  ││
│  │  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐         ││
│  │  │   Service   │  │   Service   │  │   Service   │         ││
│  │  │  :8000      │  │  :5279      │  │  :80        │         ││
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         ││
│  │         └────────────────┼────────────────┘                  ││
│  │                          │                                   ││
│  │                   ┌──────┴──────┐                           ││
│  │                   │   Ingress   │                           ││
│  │                   └──────┬──────┘                           ││
│  └──────────────────────────┼───────────────────────────────────┘│
└─────────────────────────────┼────────────────────────────────────┘
                              │
                         Internet
```

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- nginx-ingress controller (for ingress)
- cert-manager (for TLS certificates)

## Files

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates the `soarengine` namespace |
| `configmap.yaml` | Non-sensitive configuration |
| `secret.yaml` | Sensitive configuration (API keys, etc.) |
| `pvc.yaml` | Persistent storage for SQLite database |
| `api-deployment.yaml` | FastAPI backend deployment + service |
| `webhook-deployment.yaml` | .NET webhook receiver deployment + service |
| `dashboard-deployment.yaml` | React dashboard deployment + service |
| `ingress.yaml` | Ingress rules for external access |
| `kustomization.yaml` | Kustomize configuration for easy deployment |

## Quick Deploy

### Using Kustomize (Recommended)
```bash
# Preview what will be deployed
kubectl kustomize k8s/

# Deploy all resources
kubectl apply -k k8s/

# Check status
kubectl get all -n soarengine

# Delete all resources
kubectl delete -k k8s/
```

### Manual Deployment
```bash
# Create namespace first
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml

# Deploy applications
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/webhook-deployment.yaml
kubectl apply -f k8s/dashboard-deployment.yaml

# Setup ingress
kubectl apply -f k8s/ingress.yaml
```

## Configuration

### Update Secrets

Before deploying, update `secret.yaml` with your actual values:
```yaml
stringData:
  API_KEYS: "your-actual-api-key"
  ABUSEIPDB_API_KEY: "your-abuseipdb-key"
  VIRUSTOTAL_API_KEY: "your-virustotal-key"
  SLACK_WEBHOOK_URL: "your-slack-webhook-url"
```

**Important:** In production, use a secrets management solution:
- [Sealed Secrets](https://sealed-secrets.netlify.app/)
- [External Secrets Operator](https://external-secrets.io/)
- [HashiCorp Vault](https://www.vaultproject.io/)

### Update Ingress

Edit `ingress.yaml` to use your actual domain:
```yaml
spec:
  rules:
    - host: soarengine.yourdomain.com
    - host: api.soarengine.yourdomain.com
    - host: webhook.soarengine.yourdomain.com
```

## Monitoring

### Check Pod Status
```bash
kubectl get pods -n soarengine
```

### View Logs
```bash
# API logs
kubectl logs -f deployment/soarengine-api -n soarengine

# Webhook logs
kubectl logs -f deployment/soarengine-webhook -n soarengine

# Dashboard logs
kubectl logs -f deployment/soarengine-dashboard -n soarengine
```

### Check Health
```bash
# Port forward to test locally
kubectl port-forward svc/soarengine-api 8000:8000 -n soarengine

# Then access http://localhost:8000/health
```

## Scaling
```bash
# Scale API pods
kubectl scale deployment soarengine-api --replicas=5 -n soarengine

# Scale webhook pods
kubectl scale deployment soarengine-webhook --replicas=3 -n soarengine
```

## Production Recommendations

1. **Database**: Replace SQLite with PostgreSQL or a managed database service
2. **Secrets**: Use sealed-secrets or external-secrets operator
3. **Monitoring**: Add Prometheus ServiceMonitor for metrics scraping
4. **Logging**: Configure centralized logging (ELK, Loki)
5. **Network Policies**: Add network policies for pod-to-pod communication
6. **Resource Limits**: Tune resource requests/limits based on actual usage
7. **HPA**: Add Horizontal Pod Autoscaler for automatic scaling

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n soarengine
```

### Service not accessible
```bash
kubectl get endpoints -n soarengine
```

### Ingress not working
```bash
kubectl describe ingress soarengine-ingress -n soarengine
```