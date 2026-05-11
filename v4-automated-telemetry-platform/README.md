# v4 – Automated Telemetry Platform

This version evolves IndusStream from a working edge-to-cloud telemetry pipeline into a more automated and operationally mature platform.

The focus of v4 is CI/CD, telemetry data quality, automated deployment, and improved operational reliability.

---

## Objectives

- Automate Lambda deployment using GitHub Actions
- Improve telemetry validation and anomaly filtering
- Reduce manual deployment steps
- Prepare the platform for repeatable infrastructure changes
- Improve observability and failure visibility

---

## Architecture Evolution

```text
GitHub
  ↓
GitHub Actions
  ↓
Automated Lambda Deployment
  ↓
AWS IoT Core → Lambda → DynamoDB / S3 → Athena → QuickSight
```

---

## Key Additions

- CI/CD pipeline for Lambda deployment
- Cleaner analytics data before writing to S3
- Sensor anomaly filtering
- Improved deployment documentation
- Foundation for future Infrastructure as Code

---

## Planned Documentation

- [CI/CD and Automation](docs/01-ci-cd-and-automation.md)
- [Telemetry Data Quality](docs/02-telemetry-data-quality.md)
- [Operational Refresh Workflow](docs/03-operational-refresh-workflow.md)