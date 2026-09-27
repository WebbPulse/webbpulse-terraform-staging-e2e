# webbpulse-terraform-staging-e2e

Staging end-to-end test repository for WebbPulse Terraform, part of the staging
environment alongside the `webbpulse-terraform-staging-e2e` AWS account. Load
bearing for staging e2e, holds nothing durable. The staging GitHub App
`webbpulse-terraform-staging` is installed here, and the staging workspace
`first-run` is bound to `examples/first-run`.

The App's webhooks deliver each pull request and each push to `main` to
`api.staging.terraform.webbpulse.com`, which starts a plan-only run for a pull
request and a run awaiting confirmation for a push. No workflow is needed.

The configuration declares only a `random_pet`, so nothing here is billable. Open a
pull request touching `examples/first-run` to see the check runs and the pull
request comment.

The `webbpulse-terraform` aggregate check is required on `main`.

A pull request that touches nothing under `examples/first-run` still gets the
aggregate check, reported as "No runs needed", so it can merge.

