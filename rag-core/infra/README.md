# infra

AWS infrastructure as code for the RAG stack (**Terraform**).

## Contents

- **`terraform/`** — Root module: `main.tf`, `variables.tf`, `outputs.tf`, and resource files:
  - **Networking** — `vpc.tf`
  - **Compute** — `ec2.tf` (RAG host; Ray job submission, application runtime)
  - **Data** — `rds.tf` (Postgres), `s3.tf` (documents bucket)
  - **Registry** — `ecr.tf` (API and sandbox images)
  - **Serverless** — `lambda.tf` (S3-triggered ingestion; calls Ray job API on the instance)
  - **IAM** — `iam.tf`
  - **Bootstrap** — `user-data.sh.tftpl` (EC2 provisioning script)

## Configuration

Copy `terraform/terraform.tfvars.example` to `terraform.tfvars` and set:

- AWS region, environment, project name  
- RDS password (`db_password`)  
- Budget alert email (`alert_email`)  
- Your public IP CIDR for SSH (`your_ip_cidr`)  
- Optional: `rag_code_root` — filesystem path on EC2 where `rag-core` is deployed (used by Ray ingestion jobs)

## Outputs

Notable outputs include EC2 public/private IPs, RDS endpoint, S3 bucket name, ECR repository URLs, Lambda function name, and SSH key material (sensitive). Use `terraform output` after apply.

## Requirements

Terraform `>= 1.5.0`, AWS provider `~> 5.0` (see `terraform/terraform.tf`).
