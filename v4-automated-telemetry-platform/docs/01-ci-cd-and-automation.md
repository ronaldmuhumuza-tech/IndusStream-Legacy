# CI/CD and Automation

## Objective

Version 4 focuses on improving the operational side of the telemetry platform by introducing deployment automation and better engineering workflows.

The goal was to reduce manual deployment steps, improve reliability, and begin structuring the project more like a real cloud engineering environment.

## Initial Manual Deployment Model

The deployments in V3 were performed manually using the AWS Console and the VS Code AWS Toolkit.

Although this worked for testing, it introduced several risks:
- deployments were difficult to track
- changes could accidentally overwrite production code
- there was no consistent deployment process

This became more noticeable as the project grew across to version 4.

## GitHub Actions Workflow

A GitHub Actions workflow was introduced to automate Lambda deployments.

The workflow:
- triggers when code is pushed to the `v4-ci-cd-automation` branch
- packages the Lambda function
- authenticates with AWS
- deploys the updated code automatically

Workflow location:

```text
.github/workflows/deploy-lambda-dev.yml
```
## Lambda Packaging Process

The deployment package is automatically created during the workflow using a ZIP archive.

Example packaging step:

```Bash
cd v4-automated-telemetry-platform/lambda
zip -r lambda.zip .
```

This removes repetitive manual deployment steps.

### GitHub Secrets Management

AWS credentials were stored securely using GitHub Secrets.

The following secrets were configured:

* DEV_AWS_ACCESS_KEY_ID
* DEV_AWS_SECRET_ACCESS_KEY

This avoids exposing credentials directly inside the repository.

## Automated Deployment Flow

The deployment process now follows a more structured workflow:

```text
Code Change --> Git Commit --> Git Push --> GitHub Actions --> Lambda Deployment
```
This improves deployment consistency and visibility.

### DEV vs PROD Environment Strategy

One important lesson during implementation was the need to separate development and production environments.

Initially, deployments targeted the production Lambda function directly, which created operational risk during testing.

To improve this:

* the v4-ci-cd-automation branch is now used for DEV deployments
* the main branch remains the stable production branch

This introduced a safer deployment workflow.

## Workflow Validation

Several issues occurred during setup, including:

* incorrect Lambda function names
* missing AWS credentials
* workflow path problems

These were resolved using GitHub Actions logs and AWS CLI troubleshooting.

## Key learnings

Version 4 introduced practical lessons around:

- CI/CD automation - Automating Lambda deployments using GitHub Actions.
- deployment troubleshooting - Diagnosing workflow and deployment failures.
- Git branch workflows - Separating development work from stable code and /or documentation.
- AWS credential management - Managing deployment credentials securely.
- environment separation - Reducing deployment risk through DEV and PROD isolation.

It also highlighted the importance of protecting production systems during development.