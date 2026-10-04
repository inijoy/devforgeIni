variable "namespace" {
  description = "Kubernetes namespace for DevForge"
  type        = string
  default     = "default"
}

variable "release_name" {
  description = "Helm release name for the Orders Service"
  type        = string
  default     = "orders-service"
}

variable "chart_path" {
  description = "Path to the Orders Service Helm chart"
  type        = string
  default     = "../helm/orders-service"
}

variable "image_repository" {
  description = "Container image repository for the Orders Service"
  type        = string
  default     = "ghcr.io/inijoy/orders-service"
}

variable "image_tag" {
  description = "Container image tag for the Orders Service"
  type        = string
  default     = "0.2.0"
}

variable "replica_count" {
  description = "Number of Orders Service replicas"
  type        = number
  default     = 3
}