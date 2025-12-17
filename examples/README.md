# Cloudsmith Credential Helper Examples

This directory contains example implementations of credential helpers for various package managers and tools that can authenticate with Cloudsmith using the `cloudsmith tokens get` command.

## Available Examples

### Docker Credential Helper
- **Path**: `docker-credential-cloudsmith/`
- **Status**: ✅ Full implementation
- **Description**: Docker credential helper that integrates with Docker to provide automatic authentication to Cloudsmith Docker registries
- **Reference**: Similar to [amazon-ecr-credential-helper](https://github.com/awslabs/amazon-ecr-credential-helper)

### Python/pip/uv Keyring
- **Path**: `python-keyring/`
- **Status**: ✅ Full implementation
- **Description**: Python keyring backend for pip, uv, and other Python tools that use keyring for authentication
- **Reference**: Similar to [artifacts-keyring](https://github.com/microsoft/artifacts-keyring)

### Maven
- **Path**: `maven/`
- **Status**: ✅ Full implementation
- **Description**: Credential helper and configuration for Maven repositories

### Gradle
- **Path**: `gradle/`
- **Status**: ✅ Full implementation
- **Description**: Dynamic credential retrieval for Gradle builds

### Conan
- **Path**: `conan/`
- **Status**: ✅ Full implementation
- **Description**: Hook-based authentication for Conan package manager

### Conda
- **Path**: `conda/`
- **Status**: ✅ Full implementation
- **Description**: .netrc-based authentication setup for Conda

### Composer (PHP)
- **Path**: `composer/`
- **Status**: ✅ Full implementation
- **Description**: Authentication configuration for Composer

### Bundler (Ruby)
- **Path**: `ruby/`
- **Status**: ✅ Full implementation
- **Description**: Credential helper for Bundler and RubyGems

### Cargo (Rust)
- **Path**: `cargo/`
- **Status**: ✅ Full implementation
- **Description**: Credential provider for Cargo (Rust 1.68+)

### Hex (Elixir)
- **Path**: `hex/`
- **Status**: ✅ Full implementation
- **Description**: Token-based authentication for Hex

### sbt (Scala)
- **Path**: `sbt/`
- **Status**: ✅ Full implementation
- **Description**: Credential resolver for sbt builds

## Credential Helper Support by Package Manager

| Package Manager | Support Level | Implementation | Example Path |
|----------------|---------------|----------------|--------------|
| **Docker** | ✅ Native | Credential helpers | `docker-credential-cloudsmith/` |
| **Python/pip/uv** | ✅ Native | Keyring backend | `python-keyring/` |
| **Maven** | ✅ Native | Settings.xml + env vars | `maven/` |
| **Gradle** | ✅ Native | Credentials API | `gradle/` |
| **Helm** | ✅ Native | Uses Docker creds (OCI) | Uses `docker-credential-cloudsmith/` |
| **Conan** | ✅ Native | Hooks system | `conan/` |
| **Composer** | ✅ Native | Auth config | `composer/` |
| **Bundler** | ✅ Native | Bundle config | `ruby/` |
| **Cargo** | ✅ Native | Credential providers | `cargo/` |
| **sbt** | ✅ Native | Credential resolvers | `sbt/` |
| **Conda** | ⚠️  Limited | .netrc file | `conda/` |
| **Hex** | ⚠️  Limited | Env vars only | `hex/` |

✅ = Full external credential helper support  
⚠️ = Environment variables or limited support

## General Usage Pattern

All examples follow a similar pattern:

1. Detect Cloudsmith registry from request
2. Call `cloudsmith tokens get` with appropriate options
3. Return credentials in the format expected by the package manager

For OIDC-based authentication, the `--oidc-slug` option must be provided:

```bash
cloudsmith tokens get --oidc-slug my-org
```

## Quick Start

### Docker

```bash
chmod +x docker-credential-cloudsmith/docker-credential-cloudsmith
sudo cp docker-credential-cloudsmith/docker-credential-cloudsmith /usr/local/bin/
echo '{"credHelpers": {"docker.cloudsmith.io": "cloudsmith"}}' > ~/.docker/config.json
```

### Python

```bash
pip install -e python-keyring/
echo "[backend]" > ~/.config/python_keyring/keyringrc.cfg
echo "default-keyring=cloudsmith_keyring.CloudsmithKeyringBackend" >> ~/.config/python_keyring/keyringrc.cfg
```

### Maven

```bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
# Add server configuration to ~/.m2/settings.xml (see maven/README.md)
mvn deploy
```

### Gradle

```kotlin
// Add to build.gradle.kts (see gradle/README.md)
fun getCloudsmithToken() = "cloudsmith tokens get".runCommand()
```

### Cargo

```bash
chmod +x cargo/cargo-credential-cloudsmith
sudo cp cargo/cargo-credential-cloudsmith /usr/local/bin/
# Add configuration to ~/.cargo/config.toml (see cargo/README.md)
```

## Installation

See individual example directories for specific installation instructions.

## Environment Variables

Most examples support these environment variables:

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC authentication (required for OIDC)
- `CLOUDSMITH_API_KEY`: API key for authentication (alternative to OIDC)
- `CLOUDSMITH_TOKEN`: Pre-fetched token (some examples)

## Contributing

If you create credential helpers for other package managers or improve existing ones, please contribute them to this directory!
