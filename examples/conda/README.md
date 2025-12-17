# Conda Integration for Cloudsmith

Conda authentication for Cloudsmith using .netrc file.

## Installation

### Prerequisites

- Conda or Miniconda
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Setup

Conda doesn't have a native credential helper system, but it respects `.netrc` for authentication.

### Option 1: Automatic Setup Script

```bash
chmod +x setup-conda-auth.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./setup-conda-auth.sh
```

### Option 2: Manual .netrc Configuration

```bash
# Get token
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Add to .netrc
cat >> ~/.netrc << EOF
machine conda.cloudsmith.io
  login token
  password $TOKEN
EOF

chmod 600 ~/.netrc
```

## Configuration

Add Cloudsmith channel to your `.condarc`:

```yaml
channels:
  - https://conda.cloudsmith.io/my-org/my-repo/
  - defaults
```

Or use environment-specific configuration:

```yaml
channels:
  - https://conda.cloudsmith.io/my-org/my-repo/
channel_alias: https://conda.cloudsmith.io
default_channels:
  - https://conda.cloudsmith.io/my-org/my-repo/
```

## Usage

```bash
# Install package
conda install -c https://conda.cloudsmith.io/my-org/my-repo/ mypackage

# Or if configured in .condarc
conda install mypackage
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Conda Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      
    steps:
      - uses: actions/checkout@v3
      
      - uses: conda-incubator/setup-miniconda@v2
        with:
          auto-update-conda: true
          python-version: "3.10"
      
      - name: Install Cloudsmith CLI
        run: pip install cloudsmith-cli
      
      - name: Setup authentication
        run: |
          TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
          cat >> ~/.netrc << EOF
          machine conda.cloudsmith.io
            login token
            password $TOKEN
          EOF
          chmod 600 ~/.netrc
      
      - name: Install packages
        run: conda install -c https://conda.cloudsmith.io/my-org/my-repo/ mypackage
```

## Environment Variables

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC
- `CLOUDSMITH_API_KEY`: API key (alternative)

## Limitations

- Conda doesn't support external credential helpers
- .netrc tokens don't auto-refresh (need to re-run setup script periodically)
- For long-running environments, consider using cron to refresh tokens

## Token Refresh

For automated token refresh:

```bash
# Add to crontab to refresh daily
0 0 * * * /path/to/setup-conda-auth.sh
```

## Reference

- [Conda Configuration](https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/use-condarc.html)
- [.netrc Format](https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html)
- [Cloudsmith Conda Repositories](https://help.cloudsmith.io/docs/conda-repository)
