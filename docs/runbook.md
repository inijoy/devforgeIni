# DevForge Operational Runbook

## 1. Purpose

This runbook documents routine checks and basic troubleshooting for the DevForge Orders Service running on Kubernetes.

**Application:** `orders-service`  
**Application namespace:** `default`  
**Argo CD namespace:** `argocd`  
**Helm chart:** `helm/orders-service`

## 2. Check Application and GitOps Status

Check Argo CD:

```powershell
kubectl get application orders-service -n argocd
```

Expected steady state:

- Sync status: `Synced`
- Health status: `Healthy`

Check the Deployment:

```powershell
kubectl get deployment orders-service -n default
```

Check pods:

```powershell
kubectl get pods -n default
```

Check the deployed image:

```powershell
kubectl get deployment orders-service -n default -o jsonpath="{.spec.template.spec.containers[0].image}"
```

## 3. Test Application Health

Start a local port-forward:

```powershell
kubectl port-forward svc/orders-service 8000:8000 -n default
```

Keep that terminal running. In another terminal, run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response includes:

- `status`: `healthy`
- `service`: `orders-service`
- `version`: `0.2.0`

## 4. Inspect Logs and Events

View application logs:

```powershell
kubectl logs deployment/orders-service -n default
```

Inspect a pod:

```powershell
kubectl describe pod <pod-name> -n default
```

Replace `<pod-name>` with a name from `kubectl get pods -n default`.

Check recent namespace events:

```powershell
kubectl get events -n default --sort-by=.lastTimestamp
```

## 5. Check Resource Usage and Autoscaling

View pod resource usage:

```powershell
kubectl top pods -n default
```

Inspect the Horizontal Pod Autoscaler:

```powershell
kubectl get hpa orders-service -n default
kubectl describe hpa orders-service -n default
```

Configured HPA settings:

- Minimum replicas: 3
- Maximum replicas: 6
- CPU utilization target: 70%

The HPA is configured and metrics availability has been checked. Do not assume scale-up has occurred unless the observed replica count and metrics confirm it.

## 6. Validate Helm Changes

Run chart linting:

```powershell
helm lint .\helm\orders-service
```

Render the chart without deploying:

```powershell
helm template orders-service .\helm\orders-service
```

Inspect important security settings:

```powershell
helm template orders-service .\helm\orders-service | Select-String -Pattern "automountServiceAccountToken|runAsNonRoot|runAsUser|runAsGroup|allowPrivilegeEscalation|readOnlyRootFilesystem|RuntimeDefault|mountPath: /tmp"
```

## 7. Synchronize Through Argo CD

The current Argo CD Application uses manual synchronization.

After pushing a validated Helm change to the configured Git branch, check:

```powershell
kubectl get application orders-service -n argocd
```

If it reports `OutOfSync`, a sync can be requested through the Application resource using a patch file.

Create the patch:

```powershell
@'
{"operation":{"sync":{}}}
'@ | Set-Content -Path .\sync-patch.json -Encoding ascii
```

Request the sync:

```powershell
kubectl patch application orders-service -n argocd --type merge --patch-file .\sync-patch.json
```

Then watch the rollout:

```powershell
kubectl rollout status deployment/orders-service -n default --timeout=120s
```

Confirm the final Argo CD state and deployed image before considering the change complete.

The patch requests a sync; it does not guarantee that the deployment will succeed. Check pod status and logs if the rollout fails.

## 8. Troubleshooting

### Application is unhealthy

1. Check pods with `kubectl get pods -n default`.
2. Inspect the Deployment and pod events.
3. Review application logs.
4. Test `/health` using port-forwarding.

### Argo CD reports `OutOfSync`

1. Confirm the latest changes were pushed to the configured Git branch.
2. Check the Application's target revision.
3. Review the rendered Helm output.
4. Request a manual sync and verify the rollout.

### Pods fail to start

1. Inspect pod events with `kubectl describe pod`.
2. Check image name and tag.
3. Review logs where available.
4. Confirm that the security settings are compatible with the application.

### HPA does not scale

1. Check `kubectl top pods -n default`.
2. Inspect the HPA conditions and events.
3. Confirm resource requests are configured.
4. Check sustained CPU utilization against the configured target.
5. Record observed replica counts before claiming a successful scale-up test.

## 9. Security Verification

Check the pod security context:

```powershell
kubectl get deployment orders-service -n default -o jsonpath="{.spec.template.spec.securityContext}"
```

Check the container security context:

```powershell
kubectl get deployment orders-service -n default -o jsonpath="{.spec.template.spec.containers[0].securityContext}"
```

Verify that the configuration includes non-root execution, a RuntimeDefault seccomp profile, disabled privilege escalation, a read-only root filesystem, and dropped Linux capabilities.

Check the service account:

```powershell
kubectl get serviceaccount orders-service -n default -o yaml
```

Confirm that automatic token mounting is disabled.

## 10. Operational Boundaries

- Order data is held in application memory and is not persistent.
- Terraform is currently a scaffold and does not provision infrastructure.
- HPA scale-up has not been demonstrated under load.
- Full Prometheus/OpenTelemetry application monitoring and alerting are not yet implemented.
- Validate changes before synchronizing them through Argo CD.
