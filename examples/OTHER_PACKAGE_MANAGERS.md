# Credential Helper Support for Other Package Managers

This document provides information about credential helper support for various package managers and how they could integrate with `cloudsmith tokens get`.

## Supported Package Managers

### ✅ Maven

**Support**: Yes - via settings.xml with credential helper

Maven supports external credential helpers through the `maven-settings` extension.

**Example Configuration** (`~/.m2/settings.xml`):

```xml
<settings>
  <servers>
    <server>
      <id>cloudsmith</id>
      <username>token</username>
      <password>${env.CLOUDSMITH_TOKEN}</password>
    </server>
  </servers>
</settings>
```

**Integration**:
```bash
# Set token from cloudsmith CLI
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Maven will use the token from environment
mvn deploy
```

**Alternative**: Use maven-password-encryption with a script that calls `cloudsmith tokens get`.

---

### ✅ Gradle

**Support**: Yes - Credentials API

Gradle supports dynamic credentials through the Credentials API and can execute external commands.

**Example Configuration** (`build.gradle`):

```groovy
repositories {
    maven {
        url "https://maven.cloudsmith.io/my-org/my-repo/"
        credentials {
            username = "token"
            password = getCloudsmithToken()
        }
    }
}

def getCloudsmithToken() {
    def oidcSlug = System.getenv("CLOUDSMITH_OIDC_SLUG")
    def cmd = ["cloudsmith", "tokens", "get"]
    if (oidcSlug) {
        cmd += ["--oidc-slug", oidcSlug]
    }
    return cmd.execute().text.trim()
}
```

Or using Gradle properties with environment variables:

```groovy
repositories {
    maven {
        url "https://maven.cloudsmith.io/my-org/my-repo/"
        credentials {
            username = "token"
            password = System.getenv("CLOUDSMITH_TOKEN")
        }
    }
}
```

```bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
gradle publish
```

---

### ✅ Helm

**Support**: Yes - Uses Docker credential helpers

Helm 3+ stores charts in OCI registries and uses Docker's credential helper mechanism.

**Configuration**:

Since Helm uses Docker's authentication, configure the Docker credential helper (see `docker-credential-cloudsmith/`):

```bash
# Configure Docker credential helper
echo '{"credHelpers": {"docker.cloudsmith.io": "cloudsmith"}}' > ~/.docker/config.json

# Helm will automatically use Docker credentials
helm registry login docker.cloudsmith.io
helm push my-chart.tgz oci://docker.cloudsmith.io/my-org/my-repo
```

---

### ✅ Conan

**Support**: Yes - Hooks system

Conan supports hooks that can be triggered on various events, including authentication.

**Example Hook** (`~/.conan/hooks/cloudsmith_auth.py`):

```python
import os
import subprocess

def pre_download(output, reference, remote_name, **kwargs):
    """Hook called before downloading packages."""
    if "cloudsmith.io" in remote_name or "cloudsmith.io" in str(kwargs.get('url', '')):
        output.info("Getting Cloudsmith token...")
        token = get_cloudsmith_token()
        os.environ['CLOUDSMITH_TOKEN'] = token

def get_cloudsmith_token():
    """Get token from cloudsmith CLI."""
    cmd = ["cloudsmith", "tokens", "get"]
    oidc_slug = os.environ.get("CLOUDSMITH_OIDC_SLUG")
    if oidc_slug:
        cmd.extend(["--oidc-slug", oidc_slug])
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()
```

**Conan Configuration** (`~/.conan/remotes.json`):

```json
{
  "remotes": [
    {
      "name": "cloudsmith",
      "url": "https://conan.cloudsmith.io/my-org/my-repo",
      "verify_ssl": true
    }
  ]
}
```

```bash
# Authenticate (hook will get token automatically)
conan remote login cloudsmith token -p $(cloudsmith tokens get --oidc-slug my-org)
```

---

### ⚠️ Conda

**Support**: Limited - Environment variables in .condarc

Conda supports environment variable substitution in `.condarc` but doesn't have a full credential helper system.

**Configuration** (`~/.condarc`):

```yaml
channels:
  - https://conda.cloudsmith.io/my-org/my-repo

# Note: Conda doesn't support credential helpers directly
# Use environment variables or .netrc file
```

**Workaround using .netrc**:

```bash
# Generate .netrc entry
echo "machine conda.cloudsmith.io" >> ~/.netrc
echo "  login token" >> ~/.netrc
echo "  password $(cloudsmith tokens get --oidc-slug my-org)" >> ~/.netrc
chmod 600 ~/.netrc

# Conda will use .netrc for authentication
conda install -c https://conda.cloudsmith.io/my-org/my-repo my-package
```

---

### ✅ Composer (PHP)

**Support**: Yes - Auth plugins

Composer supports authentication plugins and can execute commands to retrieve credentials.

**Example using environment variables** (`composer.json`):

```json
{
  "repositories": [
    {
      "type": "composer",
      "url": "https://composer.cloudsmith.io/my-org/my-repo/"
    }
  ]
}
```

**Authentication**:

```bash
# Set token
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Configure composer
composer config http-basic.composer.cloudsmith.io token "$CLOUDSMITH_TOKEN"

# Or use global auth.json
```

**Alternative**: Create a Composer plugin that calls `cloudsmith tokens get`.

---

### ✅ Bundler (Ruby)

**Support**: Yes - Credentials from environment or bundle config

Bundler can use credentials from environment variables or bundle configuration.

**Configuration** (`Gemfile`):

```ruby
source "https://gems.cloudsmith.io/my-org/my-repo/" do
  gem "my-gem"
end
```

**Authentication**:

```bash
# Option 1: Bundle config
bundle config set --global https://gems.cloudsmith.io/my-org/my-repo/ token:$(cloudsmith tokens get --oidc-slug my-org)

# Option 2: Environment variable
export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(cloudsmith tokens get --oidc-slug my-org)"

bundle install
```

**Gemfile with credentials**:

```ruby
source "https://token:#{ENV['CLOUDSMITH_TOKEN']}@gems.cloudsmith.io/my-org/my-repo/" do
  gem "my-gem"
end
```

---

### ✅ Cargo (Rust)

**Support**: Yes - Credential providers (Cargo 1.68+)

Cargo supports credential providers for registry authentication.

**Configuration** (`~/.cargo/config.toml`):

```toml
[registries.cloudsmith]
index = "sparse+https://cargo.cloudsmith.io/my-org/my-repo/"
credential-provider = "cloudsmith-credential-provider"

[registry]
default = "cloudsmith"
```

**Credential Provider Script** (`cloudsmith-credential-provider`):

```bash
#!/bin/bash
# Cargo credential provider for Cloudsmith

case "$1" in
  get)
    # Get the registry URL from stdin
    read -r registry_url
    
    # Get token from cloudsmith CLI
    if [ -n "$CLOUDSMITH_OIDC_SLUG" ]; then
      token=$(cloudsmith tokens get --oidc-slug "$CLOUDSMITH_OIDC_SLUG")
    else
      token=$(cloudsmith tokens get)
    fi
    
    # Return in Cargo format
    echo "{\"Ok\":{\"kind\":\"token\",\"token\":\"$token\"}}"
    ;;
  *)
    echo "{\"Err\":{\"kind\":\"unsupported\"}}"
    exit 1
    ;;
esac
```

Make executable and place in PATH:
```bash
chmod +x cloudsmith-credential-provider
sudo mv cloudsmith-credential-provider /usr/local/bin/
```

---

### ⚠️ Hex (Elixir)

**Support**: Limited - Environment variables

Hex doesn't have a credential helper system but supports environment variables.

**Configuration**:

```bash
# Set token
export HEX_API_KEY=$(cloudsmith tokens get --oidc-slug my-org)

# Hex will use the environment variable
mix hex.user auth
```

**Alternative using Mix config** (`config/config.exs`):

```elixir
config :hex,
  api_url: "https://hex.cloudsmith.io/my-org/my-repo/",
  api_key: System.get_env("HEX_API_KEY")
```

---

### ✅ sbt (Scala)

**Support**: Yes - Credential resolvers

sbt supports credential resolvers that can execute external commands.

**Configuration** (`~/.sbt/1.0/credentials.sbt`):

```scala
import scala.sys.process._

credentials += {
  val token = Seq("cloudsmith", "tokens", "get", 
    sys.env.get("CLOUDSMITH_OIDC_SLUG").map(s => Seq("--oidc-slug", s)).getOrElse(Seq.empty): _*
  ).!!.trim
  
  Credentials(
    "Cloudsmith",
    "maven.cloudsmith.io",
    "token",
    token
  )
}
```

**Or using a credential provider file**:

```scala
// In build.sbt or project/plugins.sbt
credentials += {
  val token = scala.sys.process.Process("cloudsmith tokens get").!!.trim
  Credentials("Cloudsmith", "maven.cloudsmith.io", "token", token)
}
```

---

## Summary Table

| Package Manager | Method | Implementation Effort | Example Available |
|----------------|--------|---------------------|-------------------|
| Docker | Credential Helper | Low | ✅ `docker-credential-cloudsmith/` |
| Python/pip/uv | Keyring Backend | Low | ✅ `python-keyring/` |
| Maven | Settings.xml + env | Low | ⚠️ Documentation above |
| Gradle | Credentials API | Low | ⚠️ Documentation above |
| Helm | Docker creds | None | ℹ️ Uses Docker helper |
| Conan | Hooks | Medium | ⚠️ Documentation above |
| Conda | .netrc | Low | ⚠️ Documentation above |
| Composer | Config/Plugin | Medium | ⚠️ Documentation above |
| Bundler | Config/Env | Low | ⚠️ Documentation above |
| Cargo | Credential Provider | Low | ⚠️ Documentation above |
| Hex | Env vars | Low | ⚠️ Documentation above |
| sbt | Credential Resolver | Low | ⚠️ Documentation above |

**Legend:**
- ✅ Full example implementation provided
- ⚠️ Documentation and code snippets provided
- ℹ️ Uses existing credential helper
- **Low**: Simple configuration or script
- **Medium**: Requires plugin/extension development

## Contributing

If you create credential helpers for other package managers, please contribute them to this directory!
