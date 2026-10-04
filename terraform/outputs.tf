output "namespace" {
  description = "Kubernetes namespace hosting the Orders Service"
  value       = helm_release.orders_service.namespace
}

output "helm_release_name" {
  description = "Helm release name for the Orders Service"
  value       = helm_release.orders_service.name
}

output "helm_release_status" {
  description = "Current Helm release status"
  value       = helm_release.orders_service.status
}

output "orders_service_chart" {
  description = "Helm chart used for the Orders Service"
  value       = helm_release.orders_service.chart
}