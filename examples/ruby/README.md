# Ruby/Bundler Integration for Cloudsmith

Bundler authentication for Cloudsmith gem repositories.

## Installation

### Prerequisites

- Ruby and Bundler
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Configuration

### Option 1: Environment Variable (Recommended)

```bash
# Get token and set for Bundler
export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(cloudsmith tokens get --oidc-slug my-org)"

# Install gems
bundle install
```

### Option 2: Bundle Config

```bash
# Get token
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Configure bundle
bundle config set --global gems.cloudsmith.io "token:$TOKEN"

# Install
bundle install
```

### Option 3: Inline in Gemfile

**Gemfile**:
```ruby
# Get token from environment
token = ENV['CLOUDSMITH_TOKEN'] || `cloudsmith tokens get --oidc-slug my-org`.strip

source "https://token:#{token}@gems.cloudsmith.io/my-org/my-repo/" do
  gem "my-gem"
end
```

## Usage

### Gemfile Configuration

**Gemfile**:
```ruby
source "https://gems.cloudsmith.io/my-org/my-repo/" do
  gem "my-gem", "~> 1.0"
end
```

### Install Dependencies

```bash
# Set credentials
export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(cloudsmith tokens get --oidc-slug my-org)"

# Install
bundle install
```

### Publishing Gems

```bash
# Get token
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Push gem
gem push my-gem-1.0.0.gem --host https://gems.cloudsmith.io/my-org/my-repo/ \
  --credentials token:$TOKEN
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Ruby Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      
    steps:
      - uses: actions/checkout@v3
      
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: false
      
      - name: Install Cloudsmith CLI
        run: pip install cloudsmith-cli
      
      - name: Configure Bundler authentication
        run: |
          export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(cloudsmith tokens get --oidc-slug my-org)"
          echo "BUNDLE_GEMS__CLOUDSMITH__IO=$BUNDLE_GEMS__CLOUDSMITH__IO" >> $GITHUB_ENV
      
      - name: Install dependencies
        run: bundle install
```

### GitLab CI

```yaml
build:
  image: ruby:3.1
  before_script:
    - gem install bundler
    - apt-get update && apt-get install -y python3-pip
    - pip install cloudsmith-cli
    - export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(cloudsmith tokens get --oidc-slug my-org)"
  script:
    - bundle install
```

## Environment Variables

- `BUNDLE_GEMS__CLOUDSMITH__IO`: Bundler credential for gems.cloudsmith.io
- `CLOUDSMITH_TOKEN`: Pre-fetched token (alternative)
- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC
- `CLOUDSMITH_API_KEY`: API key (fallback)

## Helper Script

Use the provided Ruby helper script:

```bash
# Make executable
chmod +x cloudsmith-bundler-creds.rb

# Use in environment variable
export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(./cloudsmith-bundler-creds.rb)"

bundle install
```

## Reference

- [Bundler Configuration](https://bundler.io/man/bundle-config.1.html)
- [RubyGems Credentials](https://guides.rubygems.org/command-reference/#gem-push)
- [Cloudsmith RubyGems Repositories](https://help.cloudsmith.io/docs/ruby-repository)
