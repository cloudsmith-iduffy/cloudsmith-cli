# Conan Integration for Cloudsmith

Conan hook for Cloudsmith that automatically retrieves authentication tokens using `cloudsmith tokens get`.

## Installation

### Prerequisites

- Conan 1.x or 2.x
- Cloudsmith CLI: `pip install cloudsmith-cli`

### Setup Hook

1. Copy the hook to your Conan hooks directory:
```bash
mkdir -p ~/.conan/hooks
cp cloudsmith_auth.py ~/.conan/hooks/
```

2. Verify hooks are enabled (they are by default in Conan 1.21+):
```bash
conan config home
# Check that hooks are in ~/.conan/hooks/
```

## Configuration

### Add Cloudsmith Remote

```bash
# Add Cloudsmith remote
conan remote add cloudsmith https://conan.cloudsmith.io/my-org/my-repo/

# List remotes
conan remote list
```

### Set OIDC Slug (Optional)

For OIDC authentication, set the organization slug:

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
```

## Usage

### Installing Packages

The hook automatically authenticates when downloading:

```bash
# Set OIDC slug if using OIDC
export CLOUDSMITH_OIDC_SLUG=my-org

# Install package (hook authenticates automatically)
conan install mypackage/1.0@user/channel -r cloudsmith
```

### Uploading Packages

The hook automatically authenticates when uploading:

```bash
# Set OIDC slug if using OIDC
export CLOUDSMITH_OIDC_SLUG=my-org

# Upload package (hook authenticates automatically)
conan upload mypackage/1.0@user/channel -r cloudsmith --all
```

### Manual Authentication (Alternative)

If you prefer manual authentication instead of using the hook:

```bash
# Get token
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Login to remote
conan remote login cloudsmith token -p "$TOKEN"

# Use remote
conan install mypackage/1.0@user/channel -r cloudsmith
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Conan Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Conan and Cloudsmith CLI
        run: |
          pip install conan cloudsmith-cli
      
      - name: Install Cloudsmith hook
        run: |
          mkdir -p ~/.conan/hooks
          cp cloudsmith_auth.py ~/.conan/hooks/
      
      - name: Add Cloudsmith remote
        run: conan remote add cloudsmith https://conan.cloudsmith.io/my-org/my-repo/
      
      - name: Configure OIDC
        run: echo "CLOUDSMITH_OIDC_SLUG=my-org" >> $GITHUB_ENV
      
      - name: Build and upload
        run: |
          conan create . mypackage/1.0@user/channel
          conan upload mypackage/1.0@user/channel -r cloudsmith --all
```

### GitLab CI

```yaml
build:
  image: conanio/gcc11
  before_script:
    - pip install cloudsmith-cli
    - mkdir -p ~/.conan/hooks
    - cp cloudsmith_auth.py ~/.conan/hooks/
    - conan remote add cloudsmith https://conan.cloudsmith.io/my-org/my-repo/
    - export CLOUDSMITH_OIDC_SLUG=my-org
  script:
    - conan create . mypackage/1.0@user/channel
    - conan upload mypackage/1.0@user/channel -r cloudsmith --all
```

## Conan 2.x Configuration

For Conan 2.x, the hook system has changed. Use a different approach:

### Create a Credential Provider Script

**~/.conan2/credentials/cloudsmith.py**:
```python
import os
import subprocess


def credentials(url):
    """Get credentials for Cloudsmith URLs."""
    if "cloudsmith.io" not in url:
        return None
    
    cmd = ["cloudsmith", "tokens", "get"]
    oidc_slug = os.environ.get("CLOUDSMITH_OIDC_SLUG")
    
    if oidc_slug:
        cmd.extend(["--oidc-slug", oidc_slug])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        token = result.stdout.strip()
        return {"user": "token", "password": token}
    except:
        return None
```

### Configure global.conf

**~/.conan2/global.conf**:
```
core.sources:download:credentials_provider=cloudsmith
```

## Environment Variables

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC authentication
- `CLOUDSMITH_API_KEY`: API key (alternative to OIDC)
- `CONAN_LOGIN_USERNAME`: Set automatically by hook to "token"
- `CONAN_PASSWORD`: Set automatically by hook to the retrieved token

## Troubleshooting

### "Could not retrieve Cloudsmith token"

Ensure Cloudsmith CLI is installed:
```bash
pip install cloudsmith-cli

# Test token retrieval
cloudsmith tokens get --oidc-slug my-org
```

### Hook not running

Verify hooks are enabled:
```bash
# Check hooks directory
ls ~/.conan/hooks/

# Run with verbose output
conan install mypackage/1.0@user/channel -r cloudsmith -vv
```

### Authentication failing

Try manual authentication first:
```bash
# Get token manually
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Login manually
conan remote login cloudsmith token -p "$TOKEN"

# Then retry
conan install mypackage/1.0@user/channel -r cloudsmith
```

## How It Works

1. When Conan tries to download or upload from a Cloudsmith remote
2. The `pre_download` or `pre_upload` hook is triggered
3. Hook detects it's a Cloudsmith URL
4. Hook calls `cloudsmith tokens get` to retrieve the token
5. Hook sets environment variables for Conan to use
6. Conan proceeds with the authenticated request

## Reference

- [Conan Hooks Documentation](https://docs.conan.io/en/latest/extending/hooks.html)
- [Conan Remotes](https://docs.conan.io/en/latest/reference/commands/misc/remote.html)
- [Cloudsmith Conan Repositories](https://help.cloudsmith.io/docs/conan-repository)
