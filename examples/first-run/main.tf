terraform {
  required_version = ">= 1.11"

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    external = {
      source  = "hashicorp/external"
      version = "~> 2.3"
    }
  }
}

data "external" "long_plan" {
  program = ["sh", "-c", "sleep 1320 && echo '{\"slept\":\"1320\"}'"]
}

resource "random_pet" "first_run" {
  length = 2
}

output "greeting" {
  description = "Name the run generated, proving the plan and the apply both reached the state bucket"
  value       = random_pet.first_run.id
}
