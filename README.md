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

## Current Limitations and Next Steps

- Orders are stored in memory rather than a persistent database.
- HPA scale-up has not been demonstrated under load.
- Full application observability with Prometheus/OpenTelemetry dashboards and alerting is not yet implemented.
- Terraform infrastructure provisioning is not implemented.
- Argo CD synchronization is manual.

Possible future improvements include persistent storage, demonstrated autoscaling, application metrics and alerting, vulnerability scanning, and Terraform-managed infrastructure.

## Engineering Principles

- Automation over repetitive manual work
- Immutable, traceable container images
- GitOps-based deployment management
- Least-privilege container security
- Resource limits and health checks
- Clear operational procedures and honest verification of results
