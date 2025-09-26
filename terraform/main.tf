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

resource "aws_ecr_repository" "c19-alpha-ecr-dashboard" {
  name                 = "c19-alpha-ecr-dashboard"
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

resource "aws_iam_role_policy" "c19_alpha_lambda_to_s3_policy" {
  name = "c19_alpha_lambda_to_s3_policy"
  role = aws_iam_role.c19_alpha_lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ]
      Effect = "Allow"
      Resource = [
        "arn:aws:s3:::c19-alpha-s3-bucket",
        "arn:aws:s3:::c19-alpha-s3-bucket/*"
      ]
    }]
  })
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

# Glue Catalog DB and Glue Crawler
resource "aws_glue_catalog_database" "c19_alpha_glue_catalog_db" {
  name = "c19_alpha_glue_catalog_db"
}

resource "aws_iam_role" "c19_alpha_glue_crawler_role" {
  name = "c19_alpha_glue_crawler_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "VisualEditor0",
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "glue_crawler_s3_access" {
  name = "glue_crawler_s3_access"
  role = aws_iam_role.c19_alpha_glue_crawler_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "s3:GetObject",
        "s3:ListBucket",
      ],
      Resource = [
        "arn:aws:s3:::c19-alpha-s3-bucket",
        "arn:aws:s3:::c19-alpha-s3-bucket/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "c19_alpha_glue_crawler_policy" {
  role       = aws_iam_role.c19_alpha_glue_crawler_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_crawler" "c19_alpha_glue_crawler" {
  database_name = aws_glue_catalog_database.c19_alpha_glue_catalog_db.name
  name          = "c19_alpha_glue_crawler"
  role          = aws_iam_role.c19_alpha_glue_crawler_role.arn
  schedule      = "cron(10 0 * * ? *)"

  s3_target {
    path = "s3://${aws_s3_bucket.c19-alpha-s3-bucket.bucket}"
  }

  configuration = jsonencode(
    {
      CreatePartitionIndex = true
      Version              = 1
    }
  )
}

# ECS
resource "aws_ecs_task_definition" "c19_alpha_ecs_task_definition" {
  family                   = "c19_alpha_ecs_task_definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  task_role_arn            = aws_iam_role.c19_alpha_ecs_role.arn
  container_definitions = jsonencode([
    {
      name      = "c19_alpha_ecs_dashboard_task",
      image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-alpha-ecr-dashboard",
      cpu       = 10,
      memory    = 512,
      essential = true
      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "DB_DRIVER", value = var.DB_DRIVER },
        { name = "DB_HOST", value = var.DB_HOST },
        { name = "DB_PORT", value = var.DB_PORT },
        { name = "DB_NAME", value = var.DB_NAME },
        { name = "DB_USERNAME", value = var.DB_USERNAME },
      { name = "DB_PASSWORD", value = var.DB_PASSWORD }]
      logConfiguration = {
        logDriver = "awslogs"
        "options" : {
          awslogs-group         = "/ecs/c19_alpha_logs"
          awslogs-create-group  = "true"
          awslogs-stream-prefix = "ecs"
          awslogs-region        = "${var.AWS_REGION}"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_iam_role" "c19_alpha_ecs_role" {
  name = "c19-alpha_ecs_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "c19_alpha_ecs_athena" {
  role       = aws_iam_role.c19_alpha_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

resource "aws_iam_role_policy_attachment" "c19_alpha_ecs_rds" {
  role       = aws_iam_role.c19_alpha_ecs_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_security_group" "c19_alpha_ecs_sg" {
  name        = "c19_alpha_ecs_sg"
  description = "Allow public to access Streamlit"
  vpc_id      = "vpc-0f29b6a6ab918bcd5"

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_service" "c19_alpha_ecs_service" {
  name            = "c19_alpha_ecs_service"
  cluster         = "arn:aws:ecs:eu-west-2:129033205317:cluster/c19-ecs-cluster"
  task_definition = aws_ecs_task_definition.c19_alpha_ecs_task_definition.arn
  desired_count   = "1"

  network_configuration {
    subnets          = ["subnet-00506a8db091bdf2a"]
    security_groups  = [aws_security_group.c19_alpha_ecs_sg.id]
    assign_public_ip = true
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 100
    base              = 1
  }

  deployment_circuit_breaker {
    enable   = false
    rollback = false
  }

  deployment_configuration {
    bake_time_in_minutes = "0"
    strategy             = "ROLLING"
  }

  deployment_controller {
    type = "ECS"
  }
}
