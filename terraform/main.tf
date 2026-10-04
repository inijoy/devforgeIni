provider "helm" {
  kubernetes = {
    config_path    = "~/.kube/config"
    config_context = "minikube"
  }
}

resource "helm_release" "orders_service" {
  name      = var.release_name
  namespace = var.namespace

  chart = var.chart_path

  values = [
    yamlencode({
      replicaCount = var.replica_count

      image = {
        repository = var.image_repository
        tag        = var.image_tag
      }
    })
  ]
}