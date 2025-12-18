# Docker Credential Helper for Cloudsmith

A Docker credential helper that automatically provides authentication for Cloudsmith Docker registries using the `cloudsmith tokens get` command.

## Features

- 🔐 Automatic authentication for Cloudsmith Docker registries
- 🔄 On-demand token retrieval (no credential storage)
- 🎯 Support for API keys, SAML tokens, and OIDC authentication
- 🚀 Zero-configuration for API key and SAML users
- 🔧 OIDC support with environment variable configuration

## Installation

### Prerequisites

- Python 3.6 or later
- Cloudsmith CLI installed: `pip install cloudsmith-cli`
- Docker installed and configured

### Install the Helper

```bash
# Make the script executable
chmod +x docker-credential-cloudsmith

# Copy to a directory in your PATH
sudo cp docker-credential-cloudsmith /usr/local/bin/

# Verify installation
docker-credential-cloudsmith list
```

## Configuration

### Option 1: Global Configuration (All Registries)

Edit `~/.docker/config.json`:

```json
{
  "credsStore": "cloudsmith"
}
```

This will use the Cloudsmith credential helper for all Docker registries.

### Option 2: Per-Registry Configuration (Recommended)

Edit `~/.docker/config.json`:

```json
{
  "credHelpers": {
    "docker.cloudsmith.io": "cloudsmith"
  }
}
```

This only uses the helper for Cloudsmith registries.

### Environment Variables

For OIDC authentication, set the organization slug:

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
```

For API key authentication (if not using config file):

```bash
export CLOUDSMITH_API_KEY=your-api-key
```

## Usage

Once installed and configured, Docker will automatically use the credential helper:

```bash
# Pull from Cloudsmith
docker pull docker.cloudsmith.io/my-org/my-repo/my-image:tag

# Push to Cloudsmith
docker push docker.cloudsmith.io/my-org/my-repo/my-image:tag

# No manual login required!
```

### Manual Testing

You can test the credential helper directly:

```bash
# Test getting credentials
echo "docker.cloudsmith.io" | docker-credential-cloudsmith get

# Expected output:
# {
#   "ServerURL": "docker.cloudsmith.io",
#   "Username": "token",
#   "Secret": "your-cloudsmith-token"
# }
```

## Authentication Methods

The credential helper supports all authentication methods available in `cloudsmith tokens get`:

1. **API Key**: From `CLOUDSMITH_API_KEY` environment variable or config file
2. **SAML**: From keyring if authenticated via `cloudsmith auth`
3. **OIDC**: From environment (GitHub Actions, GitLab CI, AWS, Azure, etc.)

### OIDC Example (GitHub Actions)

```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for OIDC
      
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Cloudsmith CLI
        run: pip install cloudsmith-cli
      
      - name: Install credential helper
        run: |
          chmod +x examples/docker-credential-cloudsmith/docker-credential-cloudsmith
          sudo cp examples/docker-credential-cloudsmith/docker-credential-cloudsmith /usr/local/bin/
          mkdir -p ~/.docker
          echo '{"credHelpers": {"docker.cloudsmith.io": "cloudsmith"}}' > ~/.docker/config.json
      
      - name: Configure OIDC
        run: echo "CLOUDSMITH_OIDC_SLUG=my-org" >> $GITHUB_ENV
      
      - name: Build and push
        run: |
          docker build -t docker.cloudsmith.io/my-org/my-repo/my-image:${{ github.sha }} .
          docker push docker.cloudsmith.io/my-org/my-repo/my-image:${{ github.sha }}
```

## Troubleshooting

### "cloudsmith CLI not found"

Install the Cloudsmith CLI:
```bash
pip install cloudsmith-cli
```

### "No authentication token found"

Ensure you have authenticated using one of these methods:
```bash
# Option 1: Set API key
export CLOUDSMITH_API_KEY=your-key

# Option 2: Login via SAML
cloudsmith auth -o your-org

# Option 3: Set OIDC slug (if in OIDC-enabled environment)
export CLOUDSMITH_OIDC_SLUG=your-org
```

### "Not a Cloudsmith registry"

The helper only works with `*.cloudsmith.io` domains. For other registries, use Docker's default authentication.

## How It Works

1. Docker detects a pull/push to a Cloudsmith registry
2. Docker calls `docker-credential-cloudsmith get` with the registry URL
3. The helper calls `cloudsmith tokens get` (with `--oidc-slug` if set)
4. The token is returned to Docker in the expected format
5. Docker uses the token to authenticate with the registry

## Reference

- [Docker Credential Helpers](https://docs.docker.com/engine/reference/commandline/login/#credential-helpers)
- [Amazon ECR Credential Helper](https://github.com/awslabs/amazon-ecr-credential-helper) (similar implementation)
- [Cloudsmith Docker Registries](https://help.cloudsmith.io/docs/docker-registry)
