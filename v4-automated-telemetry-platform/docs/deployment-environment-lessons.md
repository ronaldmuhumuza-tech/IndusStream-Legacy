# 04 – Deployment Environment Lessons

This section documents lessons learned while introducing CI/CD automation into the IndusStream telemetry platform.

A test GitHub Actions deployment successfully updated the live Lambda function. This highlighted the importance of separating development and production deployment targets.

## Key Lesson

CI/CD workflows should deploy first to a DEV environment before any production deployment is allowed.

## Corrective Direction

- DEV branch/workflow deploys to DEV AWS account
- PROD deployments happen only after validation
- Lambda function names must clearly indicate environment
- Git becomes the source of truth for deployed Lambda code