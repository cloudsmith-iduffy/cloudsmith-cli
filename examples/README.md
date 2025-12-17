# Cloudsmith Credential Helper Examples

This directory contains example implementations of credential helpers for various package managers and tools that can authenticate with Cloudsmith using the `cloudsmith tokens get` command.

## Available Examples

### Docker Credential Helper
- **Path**: `docker-credential-cloudsmith/`
- **Description**: Docker credential helper that integrates with Docker to provide automatic authentication to Cloudsmith Docker registries
- **Reference**: Similar to [amazon-ecr-credential-helper](https://github.com/awslabs/amazon-ecr-credential-helper)

### Python/pip/uv Keyring
- **Path**: `python-keyring/`
- **Description**: Python keyring backend for pip, uv, and other Python tools that use keyring for authentication
- **Reference**: Similar to [artifacts-keyring](https://github.com/microsoft/artifacts-keyring)

## Credential Helper Support by Package Manager

| Package Manager | Credential Helper Support | Example Path |
|----------------|---------------------------|--------------|
| **Docker** | ✅ Yes - Credential helpers | `docker-credential-cloudsmith/` |
| **Python/pip/uv** | ✅ Yes - Keyring backend | `python-keyring/` |
| **Maven** | ✅ Yes - Settings.xml with credential helper | `maven/` |
| **Gradle** | ✅ Yes - Credentials API | `gradle/` |
| **Helm** | ✅ Yes - Registry auth (via Docker creds) | Uses Docker credential helper |
| **Conan** | ✅ Yes - Hooks system | `conan/` |
| **Conda** | ⚠️  Limited - .condarc can reference env vars | `conda/` |
| **Composer** | ✅ Yes - Auth plugins | `composer/` |
| **Ruby/Bundler** | ✅ Yes - Credentials from env or command | `ruby/` |
| **Cargo** | ✅ Yes - Credential providers | `cargo/` |
| **Hex (Elixir)** | ⚠️  Limited - Env vars in config | `hex/` |
| **sbt (Scala)** | ✅ Yes - Credential resolvers | `sbt/` |

✅ = Full external credential helper support  
⚠️ = Can reference environment variables or limited support

## General Usage Pattern

All examples follow a similar pattern:

1. Detect Cloudsmith registry from request
2. Call `cloudsmith tokens get` with appropriate options
3. Return credentials in the format expected by the package manager

For OIDC-based authentication, the `--oidc-slug` option must be provided:

```bash
cloudsmith tokens get --oidc-slug my-org
```

## Installation

See individual example directories for specific installation instructions.
