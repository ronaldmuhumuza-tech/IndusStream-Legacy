# 1. Purpose

The aim of this work was to move IndusStream from a single experimental setup into a more professional multi-environment architecture.

The DEV account is now treated as the controlled engineering environment where changes can be tested safely before any future PROD deployment.

The work covered:
* Raspberry Pi remote management
* Linux directory and file management
* Git branch and commits workflows
* DEV/PROD configuration separation
* IoT certificate separation
* MQTT topic separation
* GitHub Actions CI/CD alignment
* Lambda deployment preparation
* systemd service deployment for automated payload publishing
* DEV account cloud resource planning

# 2. Remote Access to Raspberry Pi

The Raspberry Pi is managed remotely from the Windows PC using SSH.
```Bash
ssh pi@<PI_IP_ADDRESS>
```
Once connected, commands are executed directly on the Pi to manage application files, configuration, certificates, and services.

Common checks:
```Bash
pwd
ls -la
hostname
whoami
```
# 3. Raspberry Pi Project Directory Structure

A very important architectural distinction was introduced during the environment separation work:
```text
The Raspberry Pi runtime structure should not necessarily mirror the Windows Git repository structure.
```
The Windows PC and the Raspberry Pi serve different operational roles.

## Windows PC Role

The Windows PC acts as the:
* development workstation
* Git management environment
* documentation workspace
* CI/CD control point
* infrastructure planning environment
* source-of-truth repository

Example Windows repository structure:
```Bash
        IndusStream/
         - .github/
         - local-ops/
         - v1-serverless-telemetry/
         - v2-edge-dashboard/
         - v3-edge-to-cloud/
         - v4-automated-telemetry-platform/
         - README.md
```
This structure is organised around:
* project versions
* documentation
* Git branches
* cloud deployment workflows
* architecture evolution

The repository is designed for:
* engineers
* source control
* collaboration
* version tracking
* CI/CD integration
* Raspberry Pi Role

## Raspberry Pi Role
The Raspberry Pi acts as the:
* deployed edge runtime system
* telemetry collection node
* MQTT publishing device
* operational Linux service host
* live IoT endpoint

The Pi is therefore organised around runtime operations rather than project documentation.

Recommended Pi runtime structure:
```Bash
/home/pi/indusstream/
    - config/
        - dev.env
        - prod.env
    - certs/
        - dev/
        - prod/
    - app/
        - mqtt_publisher.py
    - logs/
```
This layout is intentionally simpler and operationally focused.

The Pi structure prioritises:
* runtime stability
* configuration separation
* certificate isolation
* Linux service management
* operational troubleshooting
* resilience

The Pi should ideally contain only the components required to run the active telemetry workload.

## Relationship Between Git and the Pi

The Git repository remains the source of truth.
```text
Git repository → defines what should run
Raspberry Pi   → runs the deployed operational version
```
Typical workflow:
```text
Windows PC->Git commit->GitHub repository->Pull/update deployment on Pi->Restart runtime service
```
This separation is common in professional infrastructure environments.

The development repository may contain:
* multiple experimental versions
* documentation
* architecture diagrams
* deployment workflows
* CI/CD pipelines
* historical implementations

while the Raspberry Pi should ideally contain:
* the active application
* configuration files
* runtime certificates
* operational services
* logs

## Example of Runtime Isolation

The Git repository may contain:
```Bash
v1/
v2/
v3/
v4/
```
but the Raspberry Pi may only execute:
```Bash
/home/pi/indusstream/app/mqtt_publisher.py
```
This keeps the runtime device cleaner and easier to troubleshoot.

## Why Environment Separation Matters on the Pi

Separating DEV and PROD configuration on the Raspberry Pi reduces operational risk.

Instead of changing code directly when switching environments:
```Bash
same code
+ different config
+ different certificates
+ different MQTT topic
```
This allows:
* safer testing
* controlled promotion to PROD
* reduced accidental deployment risk
* simpler rollback
* cleaner operational governance

Example:
```Bash
DEV topic:
indusstream/dev/telemetry

PROD topic:
indusstream/prod/telemetry
```
The same publisher application can run against either environment by loading the appropriate environment configuration file.

## Local Operations Folder on Windows

The local-ops/ folder on the Windows PC can be used for:
* deployment helper scripts
* AWS operational notes
* SSH connection scripts
* Raspberry Pi helper commands
* infrastructure templates
* local automation

Example:
```Bash
local-ops/
    - aws/
    - pi/
    - scripts/
    - templates/
```
This keeps operational tooling separate from the deployed runtime environment on the Pi.

## Recommended Mental Model
```Bash
Windows PC  = engineering and source-control environment
GitHub      = central source of truth
Raspberry Pi = deployed operational edge runtime
AWS         = cloud execution and analytics platform
```
Understanding these roles is important because professional infrastructure systems are usually designed around clear operational boundaries.

The goal is not to make every machine identical.

The goal is to make each system responsible for a clearly defined role within the overall architecture.

Create directories:

The Pi was organised so that application code, configuration files, and IoT certificates are separated clearly.

Recommended structure:
```Bash
/home/pi/indusstream/
    - config/
        - dev.env
        - prod.env
    - certs/
        - dev/
            - AmazonRootCA1.pem
            - device-certificate.pem.crt
            - private.pem.key
        - prod/
            - AmazonRootCA1.pem
            - device-certificate.pem.crt
            - private.pem.key
    - app/
        - mqtt_publisher.py
```
Create directories:
```Bash
mkdir -p ~/indusstream/config
mkdir -p ~/indusstream/certs/dev
mkdir -p ~/indusstream/certs/prod
mkdir -p ~/indusstream/app
```
Verify:
```Bash
find ~/indusstream -maxdepth 3 -type d
```
# 4. Creating and Editing Files on the Pi
Create an empty file:
```Bash
touch ~/indusstream/config/dev.env
```
Edit a file using nano:
```Bash
nano ~/indusstream/config/dev.env
```
Example DEV environment file:
```Bash
AWS_IOT_ENDPOINT=<dev-iot-endpoint>
AWS_IOT_PORT=8883
AWS_IOT_TOPIC=indusstream/dev/telemetry

AWS_IOT_ROOT_CA=/home/pi/indusstream/certs/dev/AmazonRootCA1.pem
AWS_IOT_CERT=/home/pi/indusstream/certs/dev/device-certificate.pem.crt
AWS_IOT_PRIVATE_KEY=/home/pi/indusstream/certs/dev/private.pem.key

DEVICE_ID=raspberry-pi-edge-gateway-dev
ENVIRONMENT=dev
```
Example PROD environment file:
```Bash
AWS_IOT_ENDPOINT=<prod-iot-endpoint>
AWS_IOT_PORT=8883
AWS_IOT_TOPIC=indusstream/prod/telemetry

AWS_IOT_ROOT_CA=/home/pi/indusstream/certs/prod/AmazonRootCA1.pem
AWS_IOT_CERT=/home/pi/indusstream/certs/prod/device-certificate.pem.crt
AWS_IOT_PRIVATE_KEY=/home/pi/indusstream/certs/prod/private.pem.key

DEVICE_ID=raspberry-pi-edge-gateway-prod
ENVIRONMENT=prod
```
The key principle is:
```text
Same application code, different environment configuration.
```
# 5. Copying IoT Certificates to the Raspberry Pi
From the Windows PC, certificates can be copied to the Pi using scp.

Example for DEV certificates:
```Bash
scp /d/secure-config/aws/dev/iot-certs/AmazonRootCA1.pem pi@<PI_IP_ADDRESS>:/home/pi/indusstream/certs/dev/
scp /d/secure-config/aws/dev/iot-certs/device-certificate.pem.crt pi@<PI_IP_ADDRESS>:/home/pi/indusstream/certs/dev/
scp /d/secure-config/aws/dev/iot-certs/private.pem.key pi@<PI_IP_ADDRESS>:/home/pi/indusstream/certs/dev/
```
Check files on Pi:
```Bash
ls -la ~/indusstream/certs/dev
```
Secure private key permissions:
```Bash
Secure private key permissions:
chmod 600 ~/indusstream/certs/dev/private.pem.key
chmod 644 ~/indusstream/certs/dev/AmazonRootCA1.pem
chmod 644 ~/indusstream/certs/dev/device-certificate.pem.crt
```
# 6. Git Workflow Used from the Remote PC
The main project repository is managed from the Windows PC using Git Bash.

Repository location:
```Bash
cd "/d/AWS SA 2025/projects/IndusStream"
```
Check current branch and status:
```Bash
git branch
git status
```
Create and use the v4 branch:
```Bash
git checkout -b v4-ci-cd-automation
```
Stage changes:
```Bash
git add .
```
Commit changes:
```Bash
git commit -m "Add DEV environment automation structure"
```
Push changes:
```Bash
git push -u origin v4-ci-cd-automation
```
Pull latest changes:
```Bash
git pull
```
View branch history:
```Bash
git log --oneline --graph --all --decorate
```
List tracked files:
```Bash
git ls-files
```

# 7. DEV and PROD Branch Strategy
The project began moving toward this deployment model:
```Bash
v4-ci-cd-automation branch → DEV deployment
main branch                 → stable / future PROD deployment
```
The DEV branch is used for:

* experimentation
* CI/CD development
* Lambda deployment testing
* telemetry validation logic
* environment separation work

The main branch remains stable and should not receive incomplete v4 changes until documentation and validation are complete.

# 8. GitHub Actions Workflow Location
GitHub Actions workflows are stored in the standard GitHub location:
```Bash
.github/workflows/
```
DEV workflow file:
```Bash
.github/workflows/deploy-lambda-dev.yml
```
This workflow is designed to deploy to the DEV Lambda only.

Key characteristics:

* triggered by pushes to v4-ci-cd-automation
* uses DEV GitHub Secrets
* deploys to DEV Lambda
* avoids touching PROD

# 9. GitHub Secrets for DEV
DEV deployment credentials are stored in GitHub Secrets, not inside code.

Required DEV secrets:
```Bash
DEV_AWS_ACCESS_KEY_ID
DEV_AWS_SECRET_ACCESS_KEY
```
These must belong to the DEV AWS account:
```Bash
AC-TRAINING-AWS-DEVELOPMENT
Account ID: ********
```
Generic secret names such as AWS_ACCESS_KEY_ID are avoided for DEV because they increase the risk of accidentally targeting the wrong account.

# 10. AWS CLI Profiles
Local AWS CLI profiles are used to avoid accidentally running commands against the wrong AWS account.

Create DEV profile:
```Bash
aws configure --profile indusstream-dev
```
Verify DEV identity:
```Bash
aws sts get-caller-identity --profile indusstream-dev
```
Expected account:
```Bash
PROD-ACCOUNT-ID
```
Future PROD profile:
```Bash
aws configure --profile indusstream-prod
```
Expected PROD account:
```Bash
PROD-ACCOUNT-ID
```
The default CLI profile should not be trusted for deployment work.

# 11. DEV AWS Account System Blocks
A fully functional DEV environment requires the following AWS resources.

## 11.1 AWS IoT Core
Purpose:

Receives MQTT telemetry messages from the Raspberry Pi.

DEV Thing:
```Bash
raspberry-pi-edge-gateway-dev
```
DEV MQTT topic:
```Bash
indusstream/dev/telemetry
```
DEV IoT policy:
```Bash
indusstream-dev-iot-policy
```
Example IoT rule SQL:
```Bash
SELECT * FROM 'indusstream/dev/telemetry'
```
## 11.2 Lambda
Purpose:

Processes incoming telemetry, cleans readings, writes operational records to DynamoDB, writes analytics records to S3, and sends alerts through SNS.

DEV Lambda:
```Bash
indusstream_process_telemetry_dev
```
The Lambda performs:

* event parsing
* numeric cleaning
* temperature correction
* sound spike filtering
* CO estimate calculation
* DynamoDB write
* S3 analytics write
* SNS alert publishing

## 11.3 DynamoDB
Purpose:

Stores structured telemetry records for operational lookup and retention.

DEV table:
```Bash
indusstream_telemetry_dev
```
Keys:
```Bash
Partition key: device_id
Sort key: timestamp
```
TTL attribute:
```Bash
ttl
```

## 11.4 S3
Purpose:

Stores analytics-ready telemetry records for Athena and QuickSight.

DEV bucket:
```Bash
indusstream-telemetry-data-dev
```
Recommended prefixes:
```Bash
analytics/
athena-results/
quicksight/
```
Analytics records are partitioned by date:
```Bash
analytics/year=YYYY/month=MM/day=DD/
```
## 11.5 SNS
Purpose:

Sends alert notifications when sensor thresholds are exceeded.

DEV topic:
```Bash
indusstream-alerts-dev
```
Lambda environment variable:
```Bash
snstopic=<DEV SNS topic ARN>
```
## 11.6 CloudWatch Logs
Purpose:

Provides operational visibility into Lambda execution.

Used to check:
* received events
* processing errors
* permission failures
* malformed payloads
* deployment validation

# 12. Systemd Service for Automated Payload Publishing
The Raspberry Pi can run the telemetry publisher as a managed Linux service using systemd.

Create a service file:
```Bash
sudo nano /etc/systemd/system/indusstream-publisher-dev.service
```
Example service:
```Bash
[Unit]
Description=IndusStream DEV MQTT Telemetry Publisher
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/indusstream/app
EnvironmentFile=/home/pi/indusstream/config/dev.env
ExecStart=/usr/bin/python3 /home/pi/indusstream/app/mqtt_publisher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
Reload systemd:
```Bash
sudo systemctl daemon-reload
```
Enable service on boot:
```Bash
sudo systemctl enable indusstream-publisher-dev.service
```
Start service:
```Bash
sudo systemctl start indusstream-publisher-dev.service
```
Check status:
```Bash
sudo systemctl status indusstream-publisher-dev.service
```
View logs:
```Bash
journalctl -u indusstream-publisher-dev.service -n 50
```
Follow logs live:
```Bash
journalctl -u indusstream-publisher-dev.service -f
```
Restart after config/code changes:
```Bash
sudo systemctl restart indusstream-publisher-dev.service
```
Stop service:
```Bash
sudo systemctl stop indusstream-publisher-dev.service
```
# 13. End-to-End DEV Data Flow
The intended DEV system flow is:
```text
Sensors->Arduino->Raspberry Pi local app->MQTT publish to AWS IoT Core->IoT Rule->Lambda processor->DynamoDB operational record->S3 analytics record->Athena / QuickSight
```
This structure creates a professional telemetry architecture with clear responsibility at each layer.

# 14. Environment Separation Principles
DEV and PROD should use:
* separate AWS accounts
* separate IoT Things
* separate certificates
* separate MQTT topics
* separate S3 buckets
* separate DynamoDB tables
* separate Lambda functions
* separate SNS topics
* separate CLI profiles
* separate GitHub Secrets

The application code should remain mostly the same.

Only configuration should change between environments.

# 15. Current Operational Lessons
Important lessons captured during this work:

* Do not deploy workloads into the management account.
* Use DEV for CI/CD experimentation.
* Keep PROD protected until approval gates exist.
* Use named AWS CLI profiles.
* Avoid generic GitHub Secret names for multi-account deployments.
* Store IoT certificates separately from IAM access keys.
* Treat Git as the source of truth for deployed Lambda code.
* Use systemd to make Raspberry Pi services resilient and restartable.
* Standardise region usage, preferably eu-west-2 for this project.


# 16. DEV Account Completion Checklist
Before considering PROD work, the DEV environment should be fully validated end-to-end.

The objective is to ensure that the complete telemetry pipeline, deployment workflow, and edge integration architecture operate reliably inside an isolated development environment.

## AWS Account and Identity

- [ ] DEV AWS account accessible
- [ ] AWS CLI profile `indusstream-dev` configured
- [ ] `aws sts get-caller-identity --profile indusstream-dev` verified
- [ ] DEV GitHub Secrets configured
- [ ] DEV resources confirmed to exist only in `eu-west-2`

## Raspberry Pi Runtime Environment

- [ ] Raspberry Pi reachable through SSH
- [ ] `/home/pi/indusstream/` structure created
- [ ] `dev.env` configuration file created
- [ ] DEV IoT certificates copied securely
- [ ] certificate file permissions hardened
- [ ] MQTT publisher application deployed
- [ ] DEV MQTT topic configured correctly

## AWS IoT Core

- [ ] DEV Thing created
- [ ] DEV IoT policy attached
- [ ] DEV certificates activated
- [ ] IoT Rule created
- [ ] IoT Rule successfully invokes Lambda

## Lambda and Processing

- [ ] DEV Lambda created
- [ ] Lambda environment variables configured
- [ ] Lambda execution role permissions validated
- [ ] CloudWatch logs receiving events
- [ ] telemetry payload successfully processed

## Data Storage

- [ ] DynamoDB table created
- [ ] TTL enabled
- [ ] telemetry records appearing in DynamoDB
- [ ] S3 bucket created
- [ ] analytics records appearing in S3

## Alerting and Monitoring

- [ ] SNS topic created
- [ ] email subscription confirmed
- [ ] high-threshold alert successfully triggered
- [ ] CloudWatch logs reviewed for errors

## Git and CI/CD

- [ ] `v4-ci-cd-automation` branch operational
- [ ] GitHub Actions workflow validated
- [ ] DEV deployment successfully tested
- [ ] deployment isolated from PROD account
- [ ] rollback approach understood

## Operational Stability

- [ ] systemd publisher service enabled
- [ ] service restarts automatically after reboot
- [ ] service logs validated using `journalctl`
- [ ] telemetry publishing stable over time

## Environment Governance

- [ ] DEV and PROD naming conventions standardised
- [ ] separate MQTT topics implemented
- [ ] separate certificates implemented
- [ ] separate AWS resources implemented
- [ ] separate CLI profiles implemented

The DEV environment should be considered the primary engineering and validation environment.

Only after the complete DEV pipeline is operational and repeatable should PROD resources be introduced.

# 17. PROD Readiness Gate
PROD should only be built after DEV is validated end-to-end.

Before PROD deployment:
* DEV pipeline must work reliably
* branch protection should be configured
* PROD deployment should require approval
* rollback strategy should be documented
* PROD resources should be created in eu-west-2
* PROD GitHub Secrets should not be added until needed

# 18. Summary

This work transformed IndusStream from a single experimental telemetry setup into a structured multi-environment engineering platform.

The DEV account now acts as the safe engineering environment where automation, IoT ingestion, Lambda processing, data storage, and Raspberry Pi service management can be tested before anything is promoted to PROD.