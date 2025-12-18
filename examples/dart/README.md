# Dart/Pub Authentication for Cloudsmith

Configure Dart pub to authenticate with Cloudsmith package repositories using `cloudsmith tokens get`.

## Features

- ✅ Uses `dart pub token` command
- ✅ Automatic token retrieval
- ✅ Supports API key, SAML, and OIDC authentication
- ✅ CI/CD friendly

## Installation

No installation required - uses Dart's built-in `dart pub token` command.

## Configuration

### Add Cloudsmith Token

Use the wrapper script to automatically add/update tokens:

```bash
chmod +x dart-pub-with-cloudsmith.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./dart-pub-with-cloudsmith.sh get
```

### Manual Token Management

```bash
# Get token
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Add token to pub
dart pub token add https://dart.cloudsmith.io/my-org/my-repo/ --env-var CLOUDSMITH_TOKEN

# Set environment variable
export CLOUDSMITH_TOKEN="$TOKEN"
```

## Usage

### pubspec.yaml

```yaml
name: my_package
dependencies:
  my_private_package:
    hosted:
      name: my_private_package
      url: https://dart.cloudsmith.io/my-org/my-repo/
    version: ^1.0.0
```

### Get Packages

```bash
# Using wrapper script
export CLOUDSMITH_OIDC_SLUG=my-org
./dart-pub-with-cloudsmith.sh get

# Or manually
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
export CLOUDSMITH_TOKEN="$TOKEN"
dart pub get
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Get dependencies
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: |
    TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    dart pub token add https://dart.cloudsmith.io/my-org/my-repo/ --env-var CLOUDSMITH_TOKEN
    export CLOUDSMITH_TOKEN="$TOKEN"
    dart pub get
```

**GitLab CI:**
```yaml
dependencies:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    - dart pub token add https://dart.cloudsmith.io/my-org/my-repo/ --env-var CLOUDSMITH_TOKEN
    - export CLOUDSMITH_TOKEN="$TOKEN"
    - dart pub get
```

## Troubleshooting

### List configured tokens

```bash
dart pub token list
```

### Remove token

```bash
dart pub token remove https://dart.cloudsmith.io/my-org/my-repo/
```

## References

- [dart pub token Documentation](https://dart.dev/tools/pub/cmd/pub-token)
- [Cloudsmith Dart Documentation](https://help.cloudsmith.io/docs/dart-repository)
