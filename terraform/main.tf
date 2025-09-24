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
