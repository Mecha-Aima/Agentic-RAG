data "archive_file" "ingestion_lambda" {
  type        = "zip"
  source_file = "${path.module}/../../pipelines/jobs/s3_event_handler.py"
  output_path = "${path.module}/lambda_build/ingestion_trigger.zip"
}

resource "aws_lambda_function" "ingestion_trigger" {
  function_name = "${var.project_name}-ingestion-trigger"
  description   = "Submit Ray ingestion job on S3 upload"
  role          = aws_iam_role.lambda.arn
  handler       = "s3_event_handler.handle_s3_event"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 256

  filename         = data.archive_file.ingestion_lambda.output_path
  source_code_hash = data.archive_file.ingestion_lambda.output_base64sha256

  vpc_config {
    subnet_ids         = [aws_subnet.public.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      RAY_ADDRESS     = "http://${aws_instance.rag.private_ip}:8265"
      S3_BUCKET_NAME  = aws_s3_bucket.documents.bucket
      RAG_CODE_ROOT   = var.rag_code_root
      PYTHON_BIN      = "python3.11"
    }
  }

  depends_on = [
    aws_iam_role_policy.lambda_s3_read,
    aws_instance.rag,
  ]
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion_trigger.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.documents.arn
}

resource "aws_s3_bucket_notification" "documents" {
  bucket = aws_s3_bucket.documents.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".pdf"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".docx"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".txt"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.ingestion_trigger.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".html"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
