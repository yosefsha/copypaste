---
status: accepted
---

# AWS CDK (Python) as the infrastructure-as-code tool, no NAT gateway

`TASKS.md` phase 8 left the IaC tool as an open "TBD" alongside the CI/deployment work. Terraform and raw CloudFormation were the alternatives considered. Terraform was rejected because it introduces a second language/tooling ecosystem (HCL, its own state backend) for a single-contributor project already standardized on Python end to end (`ADR-004`). Raw CloudFormation was rejected as too verbose and low-level for the cross-stack wiring this app needs (VPC → ECS → ALB → CloudFront → WAF), without buying anything CDK's constructs don't already provide.

Decision: infrastructure is defined with **AWS CDK (Python)**, living in a `cdk/` directory (`app.py`, `stacks/`). `aws-cdk-lib`/`constructs` are declared as a `cdk` dependency group in the root `pyproject.toml` (`default-groups` includes it), so a single root `.venv` from `uv sync` covers the app, its tests, and the CDK tooling — simpler for a single-contributor project than maintaining a second lockfile/virtualenv. The app is split into five stacks — `PastesDataStack`, `PastesNetworkStack`, `PastesComputeStack`, `PastesWafStack`, `PastesEdgeStack` — mirroring the architecture already decided in `ADR-002` (DynamoDB) and `ADR-005` (Fargate + ALB + CloudFront), so each stack can be built, tested, and reviewed independently while `app.py` wires them together via cross-stack references.

**VPC with no NAT gateway.** Fargate tasks need outbound access (pull the container image from ECR, reach DynamoDB) but a NAT gateway costs ~$32/month before any traffic — expensive relative to a low-traffic pastebin. Instead, the VPC has only public subnets; tasks run with `assignPublicIp=True` for outbound internet access directly. Inbound exposure is closed off at the security-group level: the ALB's security group only allows inbound traffic from CloudFront's managed prefix list (`com.amazonaws.global.cloudfront.origin-facing`), so the origin is unreachable except through CloudFront, even though it sits in a public subnet.

**Custom domain/DNS is explicitly out of scope** for this pass — CloudFront's default `*.cloudfront.net` domain is used. Adding a custom domain (Route 53, ACM certificate) is straightforward to layer on later without restructuring these stacks.

Deploying (`cdk deploy`) is a separate, explicit action from writing and synthesizing (`cdk synth`) this infrastructure code — synthesizing only generates CloudFormation templates locally and makes no AWS API calls that create or modify resources, while deploying provisions real, billable infrastructure.
