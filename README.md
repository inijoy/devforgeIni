# DevForge Platform

DevForge is a cloud-native developer platform project designed to demonstrate
reliable, secure, observable, and automated application delivery using modern
platform engineering practices.

The project is being developed around a small microservices architecture and
will progressively introduce:

* Python/FastAPI services
* Automated testing
* Docker
* GitHub Actions
* GitHub Container Registry
* Kubernetes
* Helm
* Terraform
* GitOps with Argo CD
* Observability with OpenTelemetry and Prometheus
* Reliability engineering and SLOs
* Security and vulnerability management

## Architecture

Current delivery flow:

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
   +--> Docker Build
            |
            v
     GitHub Container Registry
            |
            v
       Deployable Image
```

Kubernetes deployment will be introduced as the next stage of the platform.

## Services

### Orders Service

Path: `services/orders-service`

Technology:

* Python
* FastAPI
* Pytest
* Docker

Current API endpoints:

* `GET /health`
* `GET /orders`
* `GET /orders/{order_id}`
* `POST /orders`

## Running Locally

Create and activate the Python virtual environment:

```powershell
cd services/orders-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the tests:

```powershell
python -m pytest -v
```

Start the service:

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Health check:

`http://127.0.0.1:8000/health`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Docker

Build the image:

```powershell
cd services/orders-service
docker build -t devforge/orders-service:0.1.0 .
```

Run the container:

```powershell
docker run --name orders-service -p 8000:8000 devforge/orders-service:0.1.0
```

Health check:

```powershell
curl.exe http://127.0.0.1:8000/health
```

## CI/CD

GitHub Actions automatically runs when changes are pushed to `main` or a pull request targets `main`.

The current pipeline:

1. Checks out the repository
2. Installs Python 3.14
3. Installs dependencies
4. Runs automated tests
5. Builds the Docker image
6. Authenticates to GitHub Container Registry
7. Publishes the image to GHCR

Container images are tagged using the Git commit SHA.

Example:

`ghcr.io/inijoy/orders-service:<commit-sha>`

This provides traceability between source code, CI execution, and the deployable container artifact.

## Container Registry

The Orders Service image is published to GitHub Container Registry:

`ghcr.io/inijoy/orders-service`

## Engineering Principles

DevForge is being built around the following principles:

* Automation over manual operations
* Infrastructure as Code
* Least-privilege security
* Immutable deployment artifacts
* Observability by design
* Reliability through automation and testing
* Self-service developer workflows
* Clear ownership of services throughout their lifecycle
