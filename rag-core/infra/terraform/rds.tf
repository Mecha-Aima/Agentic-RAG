resource "aws_db_subnet_group" "rag" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_db_instance" "postgres" {
  identifier     = "${var.project_name}-postgres"
  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "rag_db"
  username = "ragadmin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rag.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible          = false
  multi_az                     = false
  skip_final_snapshot          = true
  deletion_protection          = false
  performance_insights_enabled = false
  backup_retention_period      = 0

  auto_minor_version_upgrade = true
}
