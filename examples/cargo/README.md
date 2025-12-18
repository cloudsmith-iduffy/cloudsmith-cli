# Cargo Integration for Cloudsmith

Cargo credential provider for Cloudsmith Rust repositories.

## Installation

### Prerequisites

- Cargo 1.68+ (for credential provider support)
- Cloudsmith CLI: `pip install cloudsmith-cli`

### Setup Credential Provider

```bash
# Make executable
chmod +x cargo-credential-cloudsmith

# Copy to PATH
sudo cp cargo-credential-cloudsmith /usr/local/bin/
```

## Configuration

### ~/.cargo/config.toml

```toml
[registries.cloudsmith]
index = "sparse+https://cargo.cloudsmith.io/my-org/my-repo/"
credential-provider = "cloudsmith"

# Optional: Set as default registry
[registry]
default = "cloudsmith"
```

### Alternative: Token in config.toml

For Cargo < 1.68 or if you prefer not to use credential providers:

```toml
[registries.cloudsmith]
index = "sparse+https://cargo.cloudsmith.io/my-org/my-repo/"
token = "YOUR_TOKEN_HERE"
```

Update token:
```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
cargo config set registries.cloudsmith.token "$TOKEN"
```

## Usage

### Publishing Crates

**Cargo.toml**:
```toml
[package]
name = "my-crate"
version = "0.1.0"
publish = ["cloudsmith"]
```

```bash
# Set OIDC slug if needed
export CLOUDSMITH_OIDC_SLUG=my-org

# Publish (credential provider fetches token automatically)
cargo publish --registry cloudsmith
```

### Using Dependencies

**Cargo.toml**:
```toml
[dependencies]
my-dependency = { version = "1.0", registry = "cloudsmith" }
```

```bash
# Build (credential provider fetches token automatically)
export CLOUDSMITH_OIDC_SLUG=my-org
cargo build
```

## Environment Variables

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC
- `CLOUDSMITH_API_KEY`: API key (alternative)

## Troubleshooting

### "credential provider not found"

Ensure the script is in PATH:
```bash
which cargo-credential-cloudsmith
# Should output: /usr/local/bin/cargo-credential-cloudsmith
```

### Manual token configuration

For older Cargo versions or debugging:
```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
cargo config set registries.cloudsmith.token "$TOKEN"
```

## Reference

- [Cargo Credential Providers](https://doc.rust-lang.org/cargo/reference/registry-authentication.html)
- [Cargo Configuration](https://doc.rust-lang.org/cargo/reference/config.html)
- [Cloudsmith Cargo Repositories](https://help.cloudsmith.io/docs/cargo-repository)
