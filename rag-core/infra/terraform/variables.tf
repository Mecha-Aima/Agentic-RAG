variable "aws_region" {
  type        = string
  description = "AWS region for all resources"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  default     = "dev"
}

variable "project_name" {
  type        = string
  description = "Prefix for resource names"
  default     = "rag-free"
}

variable "db_password" {
  type        = string
  description = "RDS master password (ragadmin)"
  sensitive   = true
}

variable "alert_email" {
  type        = string
  description = "Email for AWS Budget notifications"
}

variable "your_ip_cidr" {
  type        = string
  description = "Your public IP with /32 for SSH and K3s API (e.g. 203.0.113.10/32)"
}

variable "rag_code_root" {
  type        = string
  description = "Path on EC2 where rag-core is synced (PYTHONPATH root for Ray ingestion jobs)"
  default     = "/opt/rag-core"
}
