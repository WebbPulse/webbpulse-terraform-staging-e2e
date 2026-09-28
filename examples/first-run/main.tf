terraform {
  required_version = ">= 1.11"

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

resource "random_pet" "first_run" {
  length = 2
}

output "greeting" {
  description = "Name the run generated, proving the plan and the apply both reached the state bucket"
  value       = random_pet.first_run.id
}

module "registry_proof" {
  source  = "staging.terraform.webbpulse.com/WebbPulse/registry-proof/null"
  version = "0.1.0"
}

output "registry_proof" {
  value = module.registry_proof.name
}
