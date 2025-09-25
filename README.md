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
can be created using the terraform script within the terraform directory.

## Getting Started

### Dependencies

### Installing

### Executing Program

## Authors
- cameronriley0 (Project Manager)
- Zephvv (Quality Assurance)
- DemoyDW (Quality Assurance)
- Tristenx (Architect)