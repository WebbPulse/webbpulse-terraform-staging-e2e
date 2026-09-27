terraform {
  required_providers {
    external = {
      source  = "hashicorp/external"
      version = "~> 2.3"
    }
  }
}

data "external" "c1_probe" {
  program = ["python3", "${path.module}/c1_probe.py"]
}

output "c1_probe" {
  value = data.external.c1_probe.result
}
