# GitHub Actions CI/CD Setup Guide

This project includes GitHub Actions workflows for automated building, testing, and deployment.

## Workflows Overview

### 1. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

This workflow runs on every push and pull request:

- **Build**: Builds all Docker images (ML Service, Frontend, Log Ingestion, Automation Service)
- **Test**: Runs tests for Python and Node.js services
- **Push to Registry**: Pushes Docker images to Docker Hub (on main branch)
- **Deploy**: Automatically deploys to your server (on main branch)

### 2. Manual Deploy (`.github/workflows/deploy.yml`)

Allows manual deployment to staging or production environments.

## Setup Instructions

### Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

#### For Docker Hub (Optional - if you want to push images)
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password or access token

#### For SSH Deployment (Required for deployment)
- `SSH_HOST`: Your server IP address or domain (e.g., `192.168.1.100` or `deploy.example.com`)
- `SSH_USERNAME`: SSH username (e.g., `root` or `ubuntu`)
- `SSH_PRIVATE_KEY`: Your private SSH key (the entire key including `-----BEGIN OPENSSH PRIVATE KEY-----`)
- `SSH_PORT`: SSH port (default: `22`, optional)
- `DEPLOY_PATH`: Path on server where code will be deployed (e.g., `/opt/aisoc`, default: `/opt/aisoc`)
- `DEPLOY_URL`: Your application URL (e.g., `https://aisoc.example.com`, optional)

### Step 2: Server Setup

On your deployment server, ensure:

1. **Docker and Docker Compose are installed**:
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Git is installed**:
   ```bash
   git --version
   ```

3. **SSH access is configured**:
   - Your SSH public key is added to `~/.ssh/authorized_keys`
   - SSH key-based authentication works

4. **Initial repository clone** (first time only):
   ```bash
   cd /opt/aisoc  # or your chosen deploy path
   git clone https://github.com/karthiktg882001/AI-SOC.git .
   ```

5. **Create `.env` file** (if needed):
   ```bash
   cd /opt/aisoc
   # Create .env with production secrets
   nano .env
   ```

### Step 3: Configure Environment Variables

If you need to override environment variables for production, you can:

1. **Create `.env` file on server** (not committed to Git)
2. **Or use GitHub Environment Secrets**:
   - Go to **Settings** → **Environments** → **New environment** → Name it `production`
   - Add environment-specific secrets there

### Step 4: Test the Workflow

1. **Push to main branch**:
   ```bash
   git push origin main
   ```

2. **Check GitHub Actions**:
   - Go to **Actions** tab in your GitHub repository
   - Watch the workflow run

3. **Manual deployment** (optional):
   - Go to **Actions** → **Deploy Application** → **Run workflow**
   - Select environment (staging/production)

## Workflow Triggers

### Automatic Triggers

- **On push to `main`**: Builds, tests, pushes to registry, and deploys
- **On push to `develop`**: Builds and tests only
- **On pull request**: Builds and tests only (no deployment)

### Manual Triggers

- **Workflow dispatch**: Run `ci-cd.yml` manually from Actions tab
- **Deploy workflow**: Run `deploy.yml` manually with environment selection

## Customization

### Change Docker Registry

If you want to use a different registry (e.g., GitHub Container Registry, AWS ECR):

1. Update the `push-to-registry` job in `.github/workflows/ci-cd.yml`
2. Change login action and image tags accordingly

### Add More Tests

Edit the `test` job in `.github/workflows/ci-cd.yml`:

```yaml
- name: Run Python tests
  run: |
    cd ml-service
    python -m pytest tests/
```

### Change Deployment Strategy

Edit the `deploy` job in `.github/workflows/ci-cd.yml` to:
- Use different deployment methods (Kubernetes, AWS, etc.)
- Add rollback mechanisms
- Include database migrations

## Troubleshooting

### Build Fails

- Check Dockerfile syntax
- Verify all dependencies are in requirements.txt/package.json
- Check GitHub Actions logs for specific errors

### Deployment Fails

1. **SSH Connection Issues**:
   - Verify `SSH_HOST`, `SSH_USERNAME`, and `SSH_PRIVATE_KEY` are correct
   - Test SSH connection manually: `ssh username@host`

2. **Permission Issues**:
   - Ensure deploy path is writable
   - Check Docker permissions on server

3. **Service Health Checks Fail**:
   - Check if ports are available
   - Verify docker-compose.yml configuration
   - Check server logs: `docker-compose logs`

### Images Not Pushing to Registry

- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set
- Check if Docker Hub account has proper permissions
- Review push logs in GitHub Actions

## Security Best Practices

1. **Never commit secrets** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Rotate SSH keys** regularly
4. **Use environment-specific secrets** for staging/production
5. **Enable branch protection** on main branch
6. **Require pull request reviews** before merging

## Monitoring

After deployment, monitor:

- GitHub Actions workflow status
- Server logs: `docker-compose logs -f`
- Service health: `docker-compose ps`
- Application endpoints

## Rollback

If deployment fails, you can rollback:

1. **On server**:
   ```bash
   cd /opt/aisoc
   git checkout <previous-commit-hash>
   docker-compose up -d --build
   ```

2. **Or use GitHub Actions** to deploy a specific commit/tag

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [SSH Action](https://github.com/appleboy/ssh-action)

