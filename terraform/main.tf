provider "aws" {
  region     = var.AWS_REGION
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
}

# S3 bucket 
resource "aws_s3_bucket" "c19-alpha-s3-bucket" {
  bucket        = "c19-alpha-s3-bucket"
  force_destroy = true
}

# ECRs
resource "aws_ecr_repository" "c19-alpha-ecr-destroy" {
  name                 = "c19-alpha-ecr-destroy"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-alpha-ecr-rds" {
  name                 = "c19-alpha-ecr-rds"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-alpha-ecr-s3" {
  name                 = "c19-alpha-ecr-s3"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Lambdas 
resource "aws_iam_role" "c19_alpha_lambda_execution_role" {
  name = "c19_alpha_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "c19_alpha_lambda_basic_execution" {
  role       = aws_iam_role.c19_alpha_lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "c19_alpha_lambda_to_s3" {
  function_name = "c19_alpha_lambda_to_s3"
  role          = aws_iam_role.c19_alpha_lambda_execution_role.arn
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-alpha-ecr-s3:latest"
  memory_size   = 512
  timeout       = 30
  architectures = ["x86_64"]

  environment {
    variables = {
      DB_DRIVER   = var.DB_DRIVER
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_NAME     = var.DB_NAME
      DB_USERNAME = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
    }
  }
}

resource "aws_lambda_function" "c19_alpha_lambda_to_rds" {
  function_name = "c19_alpha_lambda_to_rds"
  role          = aws_iam_role.c19_alpha_lambda_execution_role.arn
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-alpha-ecr-rds:latest"
  memory_size   = 512
  timeout       = 30
  architectures = ["x86_64"]

  environment {
    variables = {
      DB_DRIVER   = var.DB_DRIVER
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_NAME     = var.DB_NAME
      DB_USERNAME = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
    }
  }
}

resource "aws_lambda_function" "c19_alpha_lambda_destroy" {
  function_name = "c19_alpha_lambda_destroy"
  role          = aws_iam_role.c19_alpha_lambda_execution_role.arn
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-alpha-ecr-destroy:latest"
  memory_size   = 512
  timeout       = 30
  architectures = ["x86_64"]

  environment {
    variables = {
      DB_DRIVER   = var.DB_DRIVER
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_NAME     = var.DB_NAME
      DB_USERNAME = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
    }
  }
}
