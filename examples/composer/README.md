# Composer Plugin for Cloudsmith

Composer plugin for automatic authentication with Cloudsmith repositories using `cloudsmith tokens get`.

## Installation

### Prerequisites

- Composer 2.x
- Cloudsmith CLI: `pip install cloudsmith-cli`

### Install the Plugin

Copy the plugin script to a location where Composer can execute it:

```bash
chmod +x cloudsmith-auth.php
# Option 1: Project-specific
mkdir -p vendor/cloudsmith
cp cloudsmith-auth.php vendor/cloudsmith/

# Option 2: System-wide
sudo cp cloudsmith-auth.php /usr/local/bin/cloudsmith-composer-auth
```

## Configuration

### Option 1: Plugin Approach (Recommended - Auto Refresh)

Create a custom Composer plugin that fetches tokens dynamically.

**composer.json** (add to your project):
```json
{
  "scripts": {
    "pre-install-cmd": "@cloudsmith-auth",
    "pre-update-cmd": "@cloudsmith-auth",
    "cloudsmith-auth": [
      "php -r \"$token = trim(shell_exec('cloudsmith tokens get' . (getenv('CLOUDSMITH_OIDC_SLUG') ? ' --oidc-slug ' . getenv('CLOUDSMITH_OIDC_SLUG') : '')));  echo shell_exec('composer config http-basic.composer.cloudsmith.io token ' . $token);\"" 
    ]
  },
  "repositories": [
    {
      "type": "composer",
      "url": "https://composer.cloudsmith.io/my-org/my-repo/"
    }
  ]
}
```

This automatically fetches a fresh token before each `composer install` or `composer update`.

### Option 2: Wrapper Script

Use a wrapper that sets authentication before running composer:

**composer-with-cloudsmith.sh**:
```bash
#!/bin/bash
# Get token dynamically
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})

# Configure Composer
composer config http-basic.composer.cloudsmith.io token "$TOKEN"

# Run composer command
composer "$@"
```

Make it executable and use it:
```bash
chmod +x composer-with-cloudsmith.sh
./composer-with-cloudsmith.sh install
./composer-with-cloudsmith.sh update
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

### With Plugin (Automatic)

```bash
# Token is fetched automatically via pre-install script
composer install
```

### With Wrapper Script

```bash
./composer-with-cloudsmith.sh install
```

## Environment Variables

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC authentication (optional)
- `CLOUDSMITH_API_KEY`: API key (alternative to OIDC)

## Troubleshooting

### "The requested package could not be found"

Ensure Cloudsmith CLI is installed and token can be retrieved:
```bash
# Test token retrieval
cloudsmith tokens get --oidc-slug my-org

# Manually set auth
composer config http-basic.composer.cloudsmith.io token "$(cloudsmith tokens get --oidc-slug my-org)"
```

### "401 Unauthorized"

Token may have expired. The plugin/wrapper approach automatically refreshes tokens.

## Reference

- [Composer Authentication](https://getcomposer.org/doc/articles/authentication-for-private-packages.md)
- [Composer Scripts](https://getcomposer.org/doc/articles/scripts.md)
- [Cloudsmith Composer Repositories](https://help.cloudsmith.io/docs/composer-repository)
