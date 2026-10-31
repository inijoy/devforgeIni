# DevForge Platform

DevForge is a hands-on cloud-native platform engineering project demonstrating automated application delivery, Kubernetes deployment, GitOps, container security, and operational practices.

The project uses a FastAPI Orders Service to demonstrate the delivery lifecycle, from source code and automated tests to container publishing and Kubernetes deployment.

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
            +--> Service
            +--> Health Probes
            +--> Resource Requests/Limits
            +--> Horizontal Pod Autoscaler
```

Argo CD monitors the Git repository and deploys the Helm chart. Application changes are synchronized manually in the current configuration.

## Technology Stack

- **Application:** Python, FastAPI, Pytest
- **Containers:** Docker
- **CI/CD:** GitHub Actions
- **Container registry:** GitHub Container Registry (GHCR)
- **Orchestration:** Kubernetes
- **Packaging:** Helm
- **GitOps:** Argo CD
- **Scaling and resource metrics:** Kubernetes Metrics Server and Horizontal Pod Autoscaler
- **Infrastructure as Code:** Terraform scaffold

## Orders Service

Path: `services/orders-service/`

The service exposes the following endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service root |
| GET | `/health` | Health check |
| GET | `/orders` | List orders |
| GET | `/orders/{order_id}` | Retrieve an order |
| POST | `/orders` | Create an order |

Order data is maintained in application memory; persistent database storage is not currently implemented.

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

Argo CD Application configuration:

`argocd/application-orders-service.yaml`

The deployment includes:

- Three configured baseline replicas
- Kubernetes health probes
- CPU and memory requests and limits
- A Horizontal Pod Autoscaler configured for 3–6 replicas with a 70% CPU utilization target
- A ClusterIP Service
- A read-only container root filesystem
- Non-root execution and a RuntimeDefault seccomp profile

The HPA configuration and metrics availability have been checked. Scale-up under load has not yet been demonstrated.

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

- Non-root user: UID/GID `10001`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true`
- All Linux capabilities dropped
- `RuntimeDefault` seccomp profile
- Automatic service-account token mounting disabled
- A dedicated writable `/tmp` volume

The Helm chart passes `helm lint`.

## Terraform Status

The `terraform/` directory is currently a scaffold. Terraform validation succeeds, but the current configuration does not provision cloud infrastructure. No infrastructure provisioning should be inferred from this scaffold.

## Observability and Monitoring

The platform uses Prometheus and Grafana to monitor the Orders Service and Kubernetes workloads.

### Monitoring Stack

- **Prometheus:** Collects and stores application and infrastructure metrics.
- **Prometheus Operator:** Manages Prometheus monitoring resources.
- **ServiceMonitor:** Discovers and scrapes the Orders Service metrics endpoint.
- **Grafana:** Provides dashboards for visualizing application performance.
- **Alertmanager:** Deployed as part of the Prometheus monitoring stack.

### Application Metrics

The FastAPI Orders Service exposes Prometheus metrics through the `/metrics` endpoint.

The application uses `prometheus-fastapi-instrumentator` and `prometheus-client` for instrumentation.

Prometheus successfully discovers and scrapes all three Orders Service replicas through the configured ServiceMonitor.

### Grafana Dashboard

Dashboard: **DevForge Orders Service Monitoring**

The dashboard provides visibility into API performance through the following panels:

- **API Response Time (p95):** Tracks the 95th percentile response time.
- **API Request Rate:** Displays the rate of incoming API requests.
- **HTTP Response Status Groups:** Shows HTTP response status groups.

Example PromQL queries:

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

Start port-forwarding:

```powershell
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring
```

Access: `http://localhost:9090`

**Grafana**

Start port-forwarding:

```powershell
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Access: `http://localhost:3000`

## Current Limitations and Next Steps

- Orders are stored in application memory rather than a persistent database.
- HPA scale-up has been configured but has not yet been demonstrated under load.
- Alertmanager is deployed, but application-specific alert rules and notification delivery have not yet been demonstrated.
- Terraform infrastructure provisioning is not implemented; the current Terraform directory remains a scaffold.
- Argo CD synchronization is manual.

### Future Improvements

- Implement persistent database storage.
- Demonstrate horizontal autoscaling under load.
- Configure application-specific alert rules and notification delivery.
- Add container vulnerability scanning.
- Implement Terraform-managed infrastructure.

## Engineering Principles

- Automation over repetitive manual work
- Immutable, traceable container images
- GitOps-based deployment management
- Least-privilege container security
- Resource limits and health checks
- Clear operational procedures and honest verification of results
