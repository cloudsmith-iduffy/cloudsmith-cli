# Hex Integration for Cloudsmith

Hex authentication for Cloudsmith Elixir repositories.

## Installation

### Prerequisites

- Elixir and Mix
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Configuration

Hex doesn't have native credential helper support, so we use environment variables.

### Option 1: Environment Variable

```bash
# Get token
export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)

# Use hex
mix hex.user auth
```

### Option 2: Mix Configuration

Add to your `config/config.exs`:

```elixir
import Config

# Get token from environment
hex_token = System.get_env("CLOUDSMITH_TOKEN") || 
            case System.cmd("cloudsmith", ["tokens", "get"]) do
              {token, 0} -> String.trim(token)
              _ -> nil
            end

config :hex,
  api_url: "https://hex.cloudsmith.io/api",
  api_key: hex_token
```

### Option 3: Helper Script

Use the provided Elixir script:

```bash
chmod +x cloudsmith-hex-creds.exs
export HEX_API_KEY=$(./cloudsmith-hex-creds.exs)
```

## Usage

### Installing Packages

**mix.exs**:
```elixir
defp deps do
  [
    {:my_package, "~> 1.0", organization: "my-org"}
  ]
end
```

```bash
# Set token
export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)

# Get dependencies
mix deps.get
```

### Publishing Packages

```bash
# Set token
export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)

# Build and publish
mix hex.build
mix hex.publish --organization my-org
```

### Authenticating Hex

```bash
# Get token
export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)

# Authenticate
mix hex.user auth
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Elixir Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      
    steps:
      - uses: actions/checkout@v3
      
      - uses: erlef/setup-beam@v1
        with:
          elixir-version: '1.14'
          otp-version: '25'
      
      - name: Install Cloudsmith CLI
        run: pip install cloudsmith-cli
      
      - name: Set Hex credentials
        run: |
          export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)
          echo "HEX_API_KEY=$HEX_API_KEY" >> $GITHUB_ENV
      
      - name: Install dependencies
        run: mix deps.get
      
      - name: Build and publish
        run: |
          mix hex.build
          mix hex.publish --organization my-org --yes
```

### GitLab CI

```yaml
build:
  image: elixir:1.14
  before_script:
    - mix local.hex --force
    - apt-get update && apt-get install -y python3-pip
    - pip install cloudsmith-cli
    - export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)
  script:
    - mix deps.get
    - mix hex.build
    - mix hex.publish --organization my-org --yes
```

## Environment Variables

- `HEX_API_KEY`: Hex API key (set to Cloudsmith token)
- `CLOUDSMITH_TOKEN`: Pre-fetched token (alternative)
- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC
- `CLOUDSMITH_API_KEY`: API key (fallback)

## Token Refresh

Since Hex doesn't auto-refresh tokens, you may need to periodically update:

```bash
# Refresh token in environment
export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)

# Or create a wrapper script
cat > mix-with-cloudsmith.sh << 'EOF'
#!/bin/bash
export HEX_API_KEY=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
mix "$@"
EOF

chmod +x mix-with-cloudsmith.sh
./mix-with-cloudsmith.sh deps.get
```

## Reference

- [Hex Documentation](https://hex.pm/docs)
- [Mix Hex Tasks](https://hexdocs.pm/mix/Mix.Tasks.Hex.html)
- [Cloudsmith Hex Repositories](https://help.cloudsmith.io/docs)
