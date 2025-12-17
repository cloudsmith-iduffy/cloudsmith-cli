# Swift Package Manager Authentication for Cloudsmith

Configure Swift Package Manager to authenticate with Cloudsmith package registries using `cloudsmith tokens get`.

## Features

- ✅ Uses .netrc for authentication
- ✅ Automatic token retrieval
- ✅ Supports API key, SAML, and OIDC authentication
- ✅ macOS Keychain integration (via swift package-registry login)

## Installation

Use the setup script to configure authentication:

```bash
chmod +x setup-swift-auth.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./setup-swift-auth.sh
```

## Configuration

### Package.swift

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyApp",
    dependencies: [
        .package(
            url: "https://swift.cloudsmith.io/my-org/my-repo/my-package.git",
            from: "1.0.0"
        )
    ]
)
```

### .netrc File

The setup script creates `~/.netrc`:

```
machine swift.cloudsmith.io
login token
password <your-token>
```

## Usage

```bash
# Resolve dependencies
swift package resolve

# Build
swift build

# Update packages
swift package update
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Setup Swift authentication
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: |
    TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    echo "machine swift.cloudsmith.io login token password $TOKEN" > ~/.netrc
    chmod 600 ~/.netrc

- name: Build
  run: swift build
```

**GitLab CI:**
```yaml
build:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - TOKEN=$(cloudsmith tokens get --oidc-slug $CLOUDSMITH_OIDC_SLUG)
    - echo "machine swift.cloudsmith.io login token password $TOKEN" > ~/.netrc
    - chmod 600 ~/.netrc
    - swift build
```

## References

- [Swift Package Manager Documentation](https://docs.swift.org/package-manager/)
- [swift package-registry login](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/packageregistrylogin/)
