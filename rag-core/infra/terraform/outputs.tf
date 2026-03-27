output "ec2_public_ip" {
  description = "SSH and public API access"
  value       = aws_instance.rag.public_ip
}

output "ec2_private_ip" {
  description = "Ray dashboard / job API (Lambda uses this via env)"
  value       = aws_instance.rag.private_ip
}

output "rds_endpoint" {
  description = "RDS hostname (no port) for DATABASE_URL"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  value = aws_db_instance.postgres.port
}

output "s3_bucket_name" {
  value = aws_s3_bucket.documents.bucket
}

output "ecr_api_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecr_sandbox_repository_url" {
  value = aws_ecr_repository.sandbox.repository_url
}

output "private_key_pem" {
  description = "Save with: terraform output -raw private_key_pem > ../../deploy/rag-ec2-key.pem && chmod 600 ../../deploy/rag-ec2-key.pem"
  value       = tls_private_key.ssh.private_key_pem
  sensitive   = true
}

output "ssh_key_name" {
  value = aws_key_pair.rag.key_name
}

output "lambda_function_name" {
  value = aws_lambda_function.ingestion_trigger.function_name
}
