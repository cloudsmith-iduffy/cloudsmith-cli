# Cloudsmith Keyring Backend for Python/pip/uv

A Python keyring backend that provides automatic authentication for Cloudsmith Python repositories using the `cloudsmith tokens get` command.

## Features

- 🔐 Automatic authentication for Cloudsmith Python repositories
- 🔄 On-demand token retrieval (no credential storage)
- 🎯 Support for API keys, SAML tokens, and OIDC authentication
- 📦 Works with pip, uv, poetry, and any tool using Python keyring
- 🚀 Zero-configuration for API key and SAML users

## Installation

### Prerequisites

- Python 3.6 or later
- Cloudsmith CLI: `pip install cloudsmith-cli`
- Keyring package: `pip install keyring`

### Install the Backend

#### Option 1: Install from source (Development)

```bash
cd examples/python-keyring
pip install -e .
```

#### Option 2: Copy to site-packages

```bash
# Find your site-packages directory
python -c "import site; print(site.getsitepackages()[0])"

# Copy the backend
cp cloudsmith_keyring.py /path/to/site-packages/
```

#### Option 3: Set PYTHONPATH

```bash
export PYTHONPATH=/path/to/cloudsmith-cli/examples/python-keyring:$PYTHONPATH
```

## Configuration

### Enable the Backend

Create or edit `~/.config/python_keyring/keyringrc.cfg`:

```ini
[backend]
default-keyring=cloudsmith_keyring.CloudsmithKeyringBackend
```

Or set via environment variable:

```bash
export PYTHON_KEYRING_BACKEND=cloudsmith_keyring.CloudsmithKeyringBackend
```

### Environment Variables

For OIDC authentication:

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
```

For API key authentication:

```bash
export CLOUDSMITH_API_KEY=your-api-key
```

## Usage

### pip

Once installed and configured, pip will automatically use the keyring:

```bash
# Install from Cloudsmith
pip install --index-url https://python.cloudsmith.io/my-org/my-repo/simple/ my-package

# Or configure in pip.conf
[global]
index-url = https://python.cloudsmith.io/my-org/my-repo/simple/
```

### uv

uv also supports keyring authentication:

```bash
# Install with uv
uv pip install --index-url https://python.cloudsmith.io/my-org/my-repo/simple/ my-package
```

### poetry

Poetry uses keyring for repository authentication:

```bash
# Add Cloudsmith as a source
poetry source add cloudsmith https://python.cloudsmith.io/my-org/my-repo/simple/

# Install dependencies (keyring handles auth)
poetry install
```

### Manual Testing

Test the keyring backend directly:

```python
import keyring
from cloudsmith_keyring import CloudsmithKeyringBackend

# Set as default
keyring.set_keyring(CloudsmithKeyringBackend())

# Test getting credentials
creds = keyring.get_credential("python.cloudsmith.io", None)
print(f"Username: {creds.username}")
print(f"Password: {creds.password[:10]}...")  # Show first 10 chars
```

Or via command line:

```bash
python -c "import keyring; from cloudsmith_keyring import CloudsmithKeyringBackend; keyring.set_keyring(CloudsmithKeyringBackend()); print(keyring.get_password('python.cloudsmith.io', 'token'))"
```

## Authentication Methods

The keyring backend supports all authentication methods available in `cloudsmith tokens get`:

1. **API Key**: From `CLOUDSMITH_API_KEY` environment variable or config file
2. **SAML**: From keyring if authenticated via `cloudsmith auth`
3. **OIDC**: From environment (GitHub Actions, GitLab CI, AWS, Azure, etc.)

### OIDC Example (GitHub Actions)

```yaml
name: Python Package

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for OIDC
      
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Cloudsmith CLI and keyring
        run: |
          pip install cloudsmith-cli keyring
          pip install -e examples/python-keyring/
      
      - name: Configure keyring
        run: |
          mkdir -p ~/.config/python_keyring
          echo "[backend]" > ~/.config/python_keyring/keyringrc.cfg
          echo "default-keyring=cloudsmith_keyring.CloudsmithKeyringBackend" >> ~/.config/python_keyring/keyringrc.cfg
      
      - name: Configure OIDC
        run: echo "CLOUDSMITH_OIDC_SLUG=my-org" >> $GITHUB_ENV
      
      - name: Install dependencies
        run: pip install --index-url https://python.cloudsmith.io/my-org/my-repo/simple/ -r requirements.txt
```

## Troubleshooting

### "No module named 'keyring'"

Install the keyring package:
```bash
pip install keyring
```

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

### Backend not being used

Verify the backend is configured:
```bash
python -m keyring --list-backends
```

You should see `CloudsmithKeyringBackend` in the list.

## How It Works

1. pip (or another tool) needs credentials for a Cloudsmith repository
2. pip calls the keyring to get credentials for the URL
3. The Cloudsmith keyring backend detects it's a Cloudsmith URL
4. The backend calls `cloudsmith tokens get` (with `--oidc-slug` if set)
5. The token is returned to pip as the password
6. pip uses the token to authenticate with the repository

## Comparison with artifacts-keyring

This implementation is similar to Microsoft's artifacts-keyring but designed for Cloudsmith:

| Feature | artifacts-keyring | cloudsmith-keyring |
|---------|------------------|-------------------|
| Target | Azure Artifacts | Cloudsmith |
| Auth Methods | Azure CLI, Environment | API Key, SAML, OIDC |
| Token Source | `az artifacts` | `cloudsmith tokens get` |
| OIDC Support | Via Azure | Native (GitHub, GitLab, AWS, etc.) |

## Reference

- [Python Keyring Documentation](https://pypi.org/project/keyring/)
- [Microsoft artifacts-keyring](https://github.com/microsoft/artifacts-keyring)
- [PEP 503 - Simple Repository API](https://www.python.org/dev/peps/pep-0503/)
- [Cloudsmith Python Repositories](https://help.cloudsmith.io/docs/python-repository)
