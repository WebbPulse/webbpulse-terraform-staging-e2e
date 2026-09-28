terraform {
  required_version = ">= 1.11"

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    external = {
      source  = "hashicorp/external"
      version = "~> 2.3"
    }
  }
}

provider "aws" {}

resource "random_pet" "first_run" {
  length = 2
}

data "aws_caller_identity" "before" {}

data "external" "outlive_the_session" {
  program    = ["sh", "-c", "sleep 1200; echo '{\"slept\":\"1200\"}'"]
  depends_on = [data.aws_caller_identity.before]
}

data "aws_caller_identity" "after" {
  depends_on = [data.external.outlive_the_session]
}

output "greeting" {
  description = "Name the run generated, proving the plan and the apply both reached the state bucket"
  value       = random_pet.first_run.id
}

output "identity" {
  description = "The caller before and after sleeping past the first vended session"
  value       = "${data.aws_caller_identity.before.arn} then ${data.aws_caller_identity.after.arn}"
}
