provider "aws" {
  region     = var.AWS_REGION
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
}

resource "aws_s3_bucket" "c19-alpha-s3-bucket" {
  bucket        = "c19-alpha-s3-bucket"
  force_destroy = true
}


