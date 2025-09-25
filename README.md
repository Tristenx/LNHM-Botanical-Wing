# Plant Health Monitor
This plant monitoring system, developed for the Liverpool Natural History Museum, enables the museum to alert 
gardeners whenever issues arise. Data older than 24 hours is summarized and moved from short-term to long-term storage.

## Description
The health of each plant is monitored by a Raspberry Pi which measures various environmental factors that affect 
plant growth. The data gathered by this hardware is updated every minute and exposed via an API endpoint. This data 
is processed by a Lambda running an ETL script that runs once every minute. This script extracts, cleans, and loads the 
recordings into an RDS running Microsoft SQL Server. Once a day at midnight a step function is executed which runs 
two Lambdas in sequence. The first Lambda is an ETL script which extracts recordings from the RDS and summarizes the 
records for each plant. This summary data is then loaded into a S3 bucket for long term storage. The second Lambda is 
a script which resets the SQL Server database which allows us to keep costs down. Most of the required cloud architecture 
can be created using the terraform script within the terraform directory. Both the [Architecture Diagram](documentation/architecture_diagram.png) 
and the [ERD](documentation/database_erd.png) can be found within the documentation directory.

## Getting Started

### Dependencies
- macOS
- Docker
- Terraform
- Access to a RDS running Microsoft SQL Server
- `brew install sqlcmd`

### Installing
- Fork the Github Repository
- `git clone [URL]`

### Sample env
```
DB_HOST=xxxxx
DB_PORT=xxxxx
DB_NAME=xxxxx
DB_SCHEMA=xxxxx
DB_USERNAME=xxxxx
DB_PASSWORD=xxxxx
DB_DRIVER=xxxxx
```

### Sample terraform secrets
```
AWS_ACCESS_KEY_ID     = "xxxxx"
AWS_SECRET_ACCESS_KEY = "xxxxx"
DB_HOST               = "xxxxx"
DB_PORT               = "xxxxx"
DB_NAME               = "xxxxx"
DB_USERNAME           = "xxxxx"
DB_PASSWORD           = "xxxxx"
DB_DRIVER             = "xxxxx"
```

### Executing Program
#### Setup the database
- `cd db_etl_pipeline/`
- `bash db_setup.sh`
- `cd ..`

#### Create and push etl-rds container to ECR
- `cd api_etl_pipeline/extract-from-api/`
- `aws ecr get-login-password --region YOUR_AWS_REGION`
- `aws ecr get-login-password --region YOUR_AWS_REGION | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com`
- `docker buildx build . -t APP_NAME:latest --platform "Linux/amd64"`
- `docker tag YOUR_IMAGE_NAME:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- `docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- `cd ../..`

#### Create and push etl-s3 container to ECR
- `cd db_etl_pipeline/etl_rds_to_s3/`
- `aws ecr get-login-password --region YOUR_AWS_REGION | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com`
- `docker buildx build . -t APP_NAME:latest --platform "Linux/amd64"`
- `docker tag YOUR_IMAGE_NAME:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- `docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- `cd ../..`

#### Create and push destroy container to ECR
- `cd db_etl_pipeline/etl_rds_to_s3/reset_rds`
- `aws ecr get-login-password --region YOUR_AWS_REGION | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com`
- `docker buildx build . -t APP_NAME:latest --platform "Linux/amd64"`
- `docker tag YOUR_IMAGE_NAME:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- `docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- `cd ../../..`

#### Create AWS resources with terraform
- `cd terraform`
- `terraform init`
- `terraform apply`

#### Setup final AWS resources
- Setup an EventBridge schedule that runs the API ETL script every minute.
- Setup a Step Function which first runs the RDS ETL then the clear database script.
- Setup an EventBridge schedule that runs the Step Function once a day at midnight.


## Authors
- cameronriley0 (Project Manager)
- Zephvv (Quality Assurance)
- DemoyDW (Quality Assurance)
- Tristenx (Architect)