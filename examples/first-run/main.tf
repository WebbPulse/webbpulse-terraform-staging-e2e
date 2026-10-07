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
# tf-63 proof 1
# tf-63 proof 2
# tf-63 proof 3
# tf-63 proof 4
