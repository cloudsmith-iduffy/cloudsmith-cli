# npm Authentication for Cloudsmith

Configure npm to automatically authenticate with Cloudsmith registries using `cloudsmith tokens get`.

## Features

- ✅ Automatic token retrieval
- ✅ Scoped registry support
- ✅ Works with npm, yarn, pnpm
- ✅ Supports API key, SAML, and OIDC authentication

## Installation

### Option 1: .npmrc with Wrapper Script

Create `npm-with-cloudsmith.sh`:

```bash
#!/bin/bash
# Fetch token and configure npm
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})

# Configure authentication
npm config set //npm.cloudsmith.io/:_authToken "$TOKEN"

# Run npm command
npm "$@"
```

Make it executable:
```bash
chmod +x npm-with-cloudsmith.sh
```

### Option 2: Environment Variable in .npmrc

Create `.npmrc`:
```ini
@myscope:registry=https://npm.cloudsmith.io/my-org/my-repo/
//npm.cloudsmith.io/:_authToken=${CLOUDSMITH_TOKEN}
```

Create wrapper script:
```bash
#!/bin/bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
npm "$@"
```

## Configuration

### Project .npmrc

```ini
registry=https://registry.npmjs.org/
@myscope:registry=https://npm.cloudsmith.io/my-org/my-repo/
//npm.cloudsmith.io/:always-auth=true
```

### Environment Variables

```bash
export CLOUDSMITH_OIDC_SLUG=my-org  # For OIDC
# OR
export CLOUDSMITH_API_KEY=your-key  # For API key
```

## Usage

```bash
# Using wrapper script
export CLOUDSMITH_OIDC_SLUG=my-org
./npm-with-cloudsmith.sh install

# Publish package
./npm-with-cloudsmith.sh publish
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Install dependencies
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: |
    TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    npm config set //npm.cloudsmith.io/:_authToken "$TOKEN"
    npm install
```

**GitLab CI:**
```yaml
install:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    - npm config set //npm.cloudsmith.io/:_authToken "$TOKEN"
    - npm install
```

## References

- [npm config Documentation](https://docs.npmjs.com/cli/v10/configuring-npm/npmrc)
- [Cloudsmith npm Documentation](https://help.cloudsmith.io/docs/npm-registry)
