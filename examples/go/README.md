# Go Modules Authentication for Cloudsmith

Configure Go modules to authenticate with Cloudsmith Go module proxies using `cloudsmith tokens get`.

## Features

- ✅ Uses .netrc for authentication
- ✅ Automatic token retrieval
- ✅ Supports API key, SAML, and OIDC authentication
- ✅ Works with GOPROXY and direct module fetching

## Installation

Use the setup script to configure authentication:

```bash
chmod +x setup-go-auth.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./setup-go-auth.sh
```

## Configuration

### Environment Variables

```bash
export GOPRIVATE="go.cloudsmith.io/my-org/*"
export GOPROXY="https://go.cloudsmith.io/my-org/my-repo,https://proxy.golang.org,direct"
```

### .netrc File

The setup script creates `~/.netrc`:

```
machine go.cloudsmith.io
login token
password <your-token>
```

## Usage

```bash
# Get dependencies
go get go.cloudsmith.io/my-org/my-repo/my-package

# Build
go build

# Tidy dependencies
go mod tidy
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Setup Go authentication
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: |
    TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    echo "machine go.cloudsmith.io login token password $TOKEN" > ~/.netrc
    chmod 600 ~/.netrc
    echo "GOPRIVATE=go.cloudsmith.io/my-org/*" >> $GITHUB_ENV

- name: Build
  run: go build
```

**GitLab CI:**
```yaml
build:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    - echo "machine go.cloudsmith.io login token password $TOKEN" > ~/.netrc
    - chmod 600 ~/.netrc
    - export GOPRIVATE="go.cloudsmith.io/my-org/*"
    - go build
```

## Troubleshooting

### Verify .netrc

```bash
cat ~/.netrc
```

### Test authentication

```bash
curl -n https://go.cloudsmith.io/my-org/my-repo/my-package/@v/list
```

## References

- [Go Modules Documentation](https://go.dev/ref/mod)
- [GOPRIVATE Documentation](https://go.dev/ref/mod#private-modules)
