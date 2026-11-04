# DevForge Platform

DevForge is a hands-on cloud-native platform engineering project demonstrating application development, containerization, Kubernetes orchestration, GitOps-based delivery, observability, alerting, and infrastructure-as-code foundations.

The project uses a FastAPI Orders Service to demonstrate the software delivery lifecycle, from source code and automated testing to container publishing, Kubernetes deployment, monitoring, and operational alerting.

## Architecture

```text
Developer
   |
   v
GitHub Repository
   |
   v
GitHub Actions
   |
   +--> Automated Tests
   |
   +--> Docker Image Build
            |
            v
     GitHub Container Registry
            |
            v
      Immutable Image Tag
            |
            v
       Helm Chart in Git
            |
            v
          Argo CD
            |
            v
     Kubernetes Deployment
            |
            +--> Orders Service
            +--> Health Probes
            +--> Resource Requests/Limits
            +--> Horizontal Pod Autoscaler
            |
            v
       Prometheus
            |
            +--> Application Metrics
            +--> Kubernetes Metrics
            +--> Alert Rules
            |
            v
        Alertmanager
            |
            v
       Slack Notifications

        Grafana
            |
            +--> Application Dashboards
            +--> Kubernetes Dashboards
```

Argo CD monitors the Git repository and deploys the Helm chart. Application changes are synchronized manually in the current configuration.

## Technology Stack

- **Application:** Python, FastAPI, Pytest
- **Containers:** Docker
- **CI/CD:** GitHub Actions
- **Container Registry:** GitHub Container Registry (GHCR)
- **Orchestration:** Kubernetes
- **Packaging:** Helm
- **GitOps:** Argo CD
- **Scaling:** Kubernetes Metrics Server and Horizontal Pod Autoscaler
- **Observability:** Prometheus and Grafana
- **Alerting:** PrometheusRule and Alertmanager
- **Notifications:** Slack Incoming Webhooks
- **Infrastructure as Code:** Terraform scaffold

## Orders Service

Application path: `services/orders-service/`

The FastAPI Orders Service exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service root |
| GET | `/health` | Health check |
| GET | `/orders` | List orders |
| GET | `/orders/{order_id}` | Retrieve an order |
| POST | `/orders` | Create an order |
| GET | `/metrics` | Expose Prometheus metrics |

Order data is maintained in application memory. Persistent database storage is not currently implemented.

## Run Locally

From the repository root, create and activate a virtual environment:

```powershell
cd services/orders-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the tests:

```powershell
python -m pytest -v
```

Start the application:

```powershell
python -m uvicorn app.main:app --reload
```

Useful URLs:

- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Metrics: `http://127.0.0.1:8000/metrics`

## Docker

Build the image from the repository root:

```powershell
docker build -t devforge/orders-service:local .\services\orders-service
```

Run the container:

```powershell
docker run --rm -p 8000:8000 devforge/orders-service:local
```

Test the health endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The Docker image runs as a non-root user with UID/GID `10001`.

## CI/CD and Container Registry

GitHub Actions runs automated tests and builds and publishes the Orders Service image to GHCR when changes are pushed to `main` or a pull request targets `main`.

Published images use Git commit SHA tags:

```text
ghcr.io/inijoy/orders-service:<commit-sha>
```

This supports traceability between application source, CI execution, and deployed image versions.

## Kubernetes Deployment

The application is deployed to Kubernetes using the Helm chart at:

`helm/orders-service/`

### Argo CD GitOps Verification

Argo CD manages the Orders Service deployment using the Helm chart stored in the GitHub repository.

The Argo CD dashboard confirmed:

- Application health: Healthy.
- Synchronization status: Synced.
- Last synchronization: Sync OK.
- Git branch: `main`.
- Deployment resources: Service, ServiceAccount, Deployment, Horizontal Pod Autoscaler, ReplicaSets and Pods.

Automatic synchronization is disabled; changes are synchronized manually.

Screenshots:
- `41-argocd-orders-service-healthy-synced.png`
- `42-argocd-orders-service-resource-tree.png`

Argo CD Application configuration:

`argocd/application-orders-service.yaml`

The deployment includes:

- Three configured baseline replicas.
- Kubernetes health probes.
- CPU and memory requests and limits.
- A Horizontal Pod Autoscaler configured for 3–6 replicas with a 70% CPU utilization target.
- A ClusterIP Service.
- A read-only container root filesystem.
- Non-root execution and a RuntimeDefault seccomp profile.

During a controlled load test, CPU utilization reached 109%, and the Horizontal Pod Autoscaler increased the Orders Service replicas from 3 to 5.

### Access the application locally

Start a port-forward:

```powershell
kubectl port-forward svc/orders-service 8000:8000 -n default
```

In another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Security Baseline

The deployed container security settings include:

- Non-root user: UID/GID `10001`.
- `allowPrivilegeEscalation: false`.
- `readOnlyRootFilesystem: true`.
- All Linux capabilities dropped.
- `RuntimeDefault` seccomp profile.
- Automatic service-account token mounting disabled.
- A dedicated writable `/tmp` volume.

The Helm chart passes `helm lint`.

## Observability and Monitoring

The platform uses Prometheus and Grafana to monitor the Orders Service and Kubernetes workloads.

### Monitoring Stack

- **Prometheus:** Collects and stores application and infrastructure metrics.
- **Prometheus Operator:** Manages Prometheus monitoring resources.
- **ServiceMonitor:** Discovers and scrapes the Orders Service metrics endpoint.
- **Grafana:** Provides dashboards for application and Kubernetes performance.
- **Alertmanager:** Handles alert notifications and routing.

Prometheus successfully discovers and scrapes all three Orders Service replicas through the configured ServiceMonitor.

### Application Metrics

The FastAPI Orders Service exposes Prometheus metrics through the `/metrics` endpoint.

Instrumentation uses:

- `prometheus-fastapi-instrumentator`
- `prometheus-client`

### Grafana Dashboards

The project includes the following monitoring dashboards:

**DevForge - Orders Service API Performance**

- API Response Time (p95).
- API Request Rate.
- HTTP Response Status Groups.

Additional Kubernetes dashboards provide visibility into cluster and workload metrics, including resource utilization.

### Example PromQL Queries

**API request rate:**

```promql
sum by (handler) (
  rate(http_requests_total[5m])
)
```

**95th percentile API response time:**

```promql
histogram_quantile(
  0.95,
  sum by (le, handler) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

**HTTP response status groups:**

```promql
count by (status) (http_requests_total)
```

### Access Monitoring Interfaces

**Prometheus**

```powershell
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
```

Access: `http://localhost:9090`

**Grafana**

```powershell
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Access: `http://localhost:3000`

## Alerting and Reliability

Prometheus alert rules are defined using Kubernetes `PrometheusRule` resources.

Alert configuration:

`monitoring/alerts/orders-service-alerts.yaml`

### Application Availability Alert

The project implements the alert:

`DevForgeOrdersServiceUnavailable`

The alert monitors the number of available Orders Service deployment replicas.

It fires when the deployment has fewer than one available replica for more than one minute.

Alert severity: `critical`

### Controlled Alert Testing

The alert was tested by deliberately scaling the Orders Service deployment to zero replicas.

The test confirmed:

- Prometheus detected the unavailable deployment.
- The alert transitioned to the firing state.
- Alertmanager processed the notification.
- The firing notification was successfully delivered to the configured Slack channel.
- After restoring the deployment to three replicas, Kubernetes reported all three replicas available.
- Prometheus subsequently showed the alert as inactive.

This demonstrated alert detection, notification delivery, and recovery monitoring.

## Slack Alert Notifications

Alertmanager is configured to send application alert notifications to a dedicated Slack channel:

`#devforge-alerts`

Configuration files:

- `monitoring/alertmanager/alertmanager.yaml`
- `monitoring/alertmanager/slack-values.yaml`

The integration uses:

- Slack Incoming Webhooks.
- Kubernetes Secrets for sensitive webhook and configuration data.
- Alertmanager receiver and routing configuration.
- Helm configuration to integrate the Slack settings with the Prometheus monitoring stack.

The Slack webhook URL is stored in a Kubernetes Secret rather than committed to the Git repository.

Alertmanager is configured with `send_resolved: true` to support recovery notifications.

The firing notification delivery was verified during the controlled alert test. Recovery was confirmed in Prometheus; a distinct resolved notification in Slack has not been independently verified.

## Terraform Status

The `terraform/` directory provides an Infrastructure as Code foundation.

It currently contains Terraform configuration scaffolding, application-related variables, provider configuration, and local environment structure.

The configuration has passed Terraform formatting and validation checks.

However, the current configuration does not provision cloud infrastructure. No deployed AWS, Azure, or GCP infrastructure should be inferred from this scaffold.

Application delivery and Kubernetes deployment are currently managed through Helm and Argo CD.

## Current Limitations and Next Steps

- Orders are stored in application memory rather than a persistent database.
- HPA scale-up has been demonstrated under controlled load; further validation of scale-down behaviour remains outstanding.
- A distinct Slack recovery notification has not yet been independently verified.
- Terraform infrastructure provisioning is not implemented.
- Argo CD synchronization is manual.
- Container vulnerability scanning has not yet been integrated.

### Future Improvements

- Implement persistent database storage.
- Validate HPA scale-down behaviour.
- Verify distinct Slack recovery notifications.
- Implement Terraform-managed infrastructure.
- Add container vulnerability scanning.
- Explore automated GitOps synchronization.

## Engineering Principles

- Automation over repetitive manual work.
- Immutable, traceable container images.
- GitOps-based deployment management.
- Least-privilege container security.
- Resource limits and health checks.
- Observability-driven operations.
- Secure handling of application secrets.
- Clear operational procedures and honest verification of results.