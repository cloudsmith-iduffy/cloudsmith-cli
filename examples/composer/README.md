# Composer Integration for Cloudsmith

Composer authentication for Cloudsmith repositories.

## Installation

### Prerequisites

- Composer 2.x
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Configuration

### Option 1: Environment Variable (Recommended)

```bash
# Get token
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Configure Composer
composer config --global http-basic.composer.cloudsmith.io token "$CLOUDSMITH_TOKEN"
```

### Option 2: Auth.json

Create or update `~/.composer/auth.json`:

```json
{
  "http-basic": {
    "composer.cloudsmith.io": {
      "username": "token",
      "password": "YOUR_TOKEN_HERE"
    }
  }
}
```

Update with fresh token:
```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
composer config --global http-basic.composer.cloudsmith.io token "$TOKEN"
```

### Option 3: Inline in composer.json

**Not recommended for security**, but possible:

```json
{
  "repositories": [
    {
      "type": "composer",
      "url": "https://composer.cloudsmith.io/my-org/my-repo/",
      "options": {
        "http": {
          "header": [
            "Authorization: Bearer ${CLOUDSMITH_TOKEN}"
          ]
        }
      }
    }
  ]
}
```

## Usage

### Adding Cloudsmith Repository

**composer.json**:
```json
{
  "repositories": [
    {
      "type": "composer",
      "url": "https://composer.cloudsmith.io/my-org/my-repo/"
    }
  ],
  "require": {
    "vendor/package": "^1.0"
  }
}
```

### Install Dependencies

```bash
# Set token
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
composer config http-basic.composer.cloudsmith.io token "$CLOUDSMITH_TOKEN"

# Install
composer install
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Composer Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      
    steps:
      - uses: actions/checkout@v3
      
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.1'
          tools: composer
      
      - name: Install Cloudsmith CLI
        run: pip install cloudsmith-cli
      
      - name: Configure Composer authentication
        run: |
          TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
          composer config http-basic.composer.cloudsmith.io token "$TOKEN"
      
      - name: Install dependencies
        run: composer install
```

### GitLab CI

```yaml
build:
  image: composer:latest
  before_script:
    - apk add --no-cache python3 py3-pip
    - pip install cloudsmith-cli
    - TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
    - composer config http-basic.composer.cloudsmith.io token "$TOKEN"
  script:
    - composer install
```

## Environment Variables

- `CLOUDSMITH_TOKEN`: Pre-fetched token
- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC
- `CLOUDSMITH_API_KEY`: API key (alternative)

## Reference

- [Composer Authentication](https://getcomposer.org/doc/articles/authentication-for-private-packages.md)
- [Cloudsmith Composer Repositories](https://help.cloudsmith.io/docs/composer-repository)
