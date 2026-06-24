# Infrastructure as Code

> Terraform, Helm, GitOps — every infra change is a PR.

## Why IaC

- **Reproducibility** — same code rebuilds dev / staging / prod.
- **Review** — infra changes go through PR.
- **Disaster recovery** — `terraform apply` in another region rebuilds the world.

## Terraform in 50 lines

[Terraform](https://developer.hashicorp.com/terraform) is the dominant IaC tool.

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "tf-state-prod"
    key    = "neuro-handbook/main.tfstate"
    region = "us-east-1"
  }
}

provider "aws" { region = "us-east-1" }

resource "aws_s3_bucket" "bids" { bucket = "lab-bids-prod" }

resource "aws_s3_bucket_versioning" "bids" {
  bucket = aws_s3_bucket.bids.id
  versioning_configuration { status = "Enabled" }
}
```

`terraform plan` shows the diff; `terraform apply` makes it real.

## State

- Store remotely (S3 + DynamoDB lock, or Terraform Cloud).
- Never edit by hand; use `terraform import` and `terraform state mv`.
- Lock during apply.

## Modules

Reusable components, composed in environment configs (`environments/prod/main.tf`).

## Kubernetes packaging — Helm

[Helm](https://helm.sh/docs/) charts package YAML with values:

```yaml
replicaCount: 3
image:
  repository: ghcr.io/lab/pipeline
  tag: v1.4.2
resources:
  limits: { cpu: 4, memory: 16Gi }
```

`helm upgrade --install pipeline ./chart -f values.prod.yaml`.

## GitOps — Argo CD / Flux

Instead of CI pushing to the cluster, an agent in the cluster pulls from git. [Argo CD](https://argo-cd.readthedocs.io/) and [Flux](https://fluxcd.io/) are the leaders.

Benefits: full audit trail, rollback by `git revert`, no CI credentials in cluster.

## References

1. **Brikman Y.** *Terraform: Up & Running.* 3rd ed. O'Reilly; 2022. ISBN 978-1098116743.
2. **The Twelve-Factor App.** [https://12factor.net/](https://12factor.net/)
3. **OpenGitOps Principles.** [https://opengitops.dev](https://opengitops.dev)

## Where to next

[Cohort-scale pipelines](cohort-scale.md) — the operational patterns IaC is most often used to provision for in neuroimaging contexts.
