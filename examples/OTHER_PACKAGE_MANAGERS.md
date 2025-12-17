# Credential Helper Support for Other Package Managers

This document provides information about credential helper support for various package managers and how they integrate with `cloudsmith tokens get`.

## Supported Package Managers

### ✅ Maven

**Support**: Yes - via settings.xml with credential helper

Maven supports external credential helpers through wrapper scripts that dynamically fetch tokens.

**Recommended Approach** - Wrapper Script:

Create `mvn-with-cloudsmith.sh`:
```bash
#!/bin/bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
mvn "$@"
```

**~/.m2/settings.xml**:
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

**Usage**:
```bash
chmod +x mvn-with-cloudsmith.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./mvn-with-cloudsmith.sh deploy
```

---

### ✅ Gradle

**Support**: Yes - Credentials API

Gradle supports dynamic credentials through the Credentials API and can execute external commands directly in the build script.

**Configuration** (`build.gradle.kts`):

```kotlin
import java.io.ByteArrayOutputStream

fun getCloudsmithToken(): String {
    val oidcSlug = System.getenv("CLOUDSMITH_OIDC_SLUG")
    val cmd = mutableListOf("cloudsmith", "tokens", "get")
    
    if (oidcSlug != null && oidcSlug.isNotEmpty()) {
        cmd.addAll(listOf("--oidc-slug", oidcSlug))
    }
    
    val stdout = ByteArrayOutputStream()
    exec {
        commandLine = cmd
        standardOutput = stdout
    }
    return stdout.toString().trim()
}

repositories {
    maven {
        name = "Cloudsmith"
        url = uri("https://maven.cloudsmith.io/my-org/my-repo/")
        credentials {
            username = "token"
            password = getCloudsmithToken()
        }
    }
}
```

Or for Groovy (`build.gradle`):

```groovy
def getCloudsmithToken() {
    def oidcSlug = System.getenv("CLOUDSMITH_OIDC_SLUG")
    def cmd = ["cloudsmith", "tokens", "get"]
    
    if (oidcSlug) {
        cmd += ["--oidc-slug", oidcSlug]
    }
    
    def stdout = new ByteArrayOutputStream()
    exec {
        commandLine cmd
        standardOutput = stdout
    }
    return stdout.toString().trim()
}

repositories {
    maven {
        name = "Cloudsmith"
        url = "https://maven.cloudsmith.io/my-org/my-repo/"
        credentials {
            username = "token"
            password = getCloudsmithToken()
        }
    }
}
```

---

### ✅ Helm

**Support**: Yes - Uses Docker credential helpers

**Helm 3+ (OCI Registries)**:

Helm 3+ stores charts in OCI registries and uses Docker's credential helper mechanism.

Since Helm uses Docker's authentication, configure the Docker credential helper (see `docker-credential-cloudsmith/`):

```bash
# Configure Docker credential helper
echo '{"credHelpers": {"docker.cloudsmith.io": "cloudsmith"}}' > ~/.docker/config.json

# Helm will automatically use Docker credentials
helm registry login docker.cloudsmith.io
helm push my-chart.tgz oci://docker.cloudsmith.io/my-org/my-repo
```

**Helm 2 (Classic/HTTP Repositories)**:

Helm 2 uses traditional HTTP-based chart repositories. Use basic auth with dynamically fetched tokens:

```bash
# Fetch token
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Add repository with authentication
helm repo add cloudsmith https://charts.cloudsmith.io/my-org/my-repo/ \
  --username token \
  --password "$TOKEN"

# Install chart
helm install my-release cloudsmith/my-chart
```

**Note**: Helm 2 tokens will expire (default 12 hours). You'll need to update the repository credentials periodically or use a wrapper script.

---

### ✅ Conan

**Support**: Yes - Hooks system

Conan supports hooks that can be triggered on various events, including authentication.

**Hook Implementation** (`~/.conan/hooks/cloudsmith_auth.py`):

```python
import os
import subprocess

def get_cloudsmith_token():
    """Get token from cloudsmith CLI."""
    cmd = ["cloudsmith", "tokens", "get"]
    oidc_slug = os.environ.get("CLOUDSMITH_OIDC_SLUG")
    if oidc_slug:
        cmd.extend(["--oidc-slug", oidc_slug])
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()

def pre_download(output, reference, remote_name, **kwargs):
    """Hook called before downloading packages."""
    if "cloudsmith.io" in remote_name or "cloudsmith.io" in str(kwargs.get('url', '')):
        output.info("Getting Cloudsmith token...")
        token = get_cloudsmith_token()
        # Note: This sets CONAN_LOGIN_USERNAME and CONAN_PASSWORD for Conan to use
        # These are environment variables that Conan reads, not specific to cloudsmith CLI
        os.environ['CONAN_LOGIN_USERNAME'] = 'token'
        os.environ['CONAN_PASSWORD'] = token
```

**Note**: The `CONAN_LOGIN_USERNAME` and `CONAN_PASSWORD` environment variables are read by Conan itself during authentication, not by the cloudsmith CLI. This is Conan's standard mechanism for providing credentials.

---

### ✅ Composer (PHP)

**Support**: Yes - Can execute commands via wrapper scripts

**Recommended Approach** - Wrapper Script:

Create `composer-with-cloudsmith.sh`:
```bash
#!/bin/bash
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
composer config http-basic.composer.cloudsmith.io token "$TOKEN"
composer "$@"
```

**Usage**:
```bash
chmod +x composer-with-cloudsmith.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./composer-with-cloudsmith.sh install
```

**composer.json**:
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

---

### ✅ Cargo (Rust)

**Support**: Yes - Credential providers (Cargo 1.68+)

Cargo supports credential providers for registry authentication.

**Credential Provider Script** (`cargo-credential-cloudsmith`):

```bash
#!/bin/bash
# Cargo credential provider for Cloudsmith

case "$1" in
  get)
    if [ -n "$CLOUDSMITH_OIDC_SLUG" ]; then
      TOKEN=$(cloudsmith tokens get --oidc-slug "$CLOUDSMITH_OIDC_SLUG")
    else
      TOKEN=$(cloudsmith tokens get)
    fi
    
    if [ -z "$TOKEN" ]; then
      echo '{"Err":{"kind":"other","message":"Failed to get Cloudsmith token"}}'
      exit 1
    fi
    
    echo "{\"Ok\":{\"kind\":\"token\",\"token\":\"$TOKEN\",\"cache\":\"session\"}}"
    ;;
  *)
    echo '{"Err":{"kind":"unsupported-command"}}'
    exit 1
    ;;
esac
```

**Configuration** (`~/.cargo/config.toml`):
```toml
[registries.cloudsmith]
index = "sparse+https://cargo.cloudsmith.io/my-org/my-repo/"
credential-provider = "cloudsmith"
```

Install the provider:
```bash
chmod +x cargo-credential-cloudsmith
sudo cp cargo-credential-cloudsmith /usr/local/bin/
```

---

### ✅ sbt (Scala)

**Support**: Yes - Credential resolvers

sbt supports credential resolvers that can execute external commands.

**Configuration** (`~/.sbt/1.0/credentials.sbt`):

```scala
import scala.sys.process._
import scala.util.Try

lazy val getCloudsmithToken: String = {
  val oidcSlug = sys.env.get("CLOUDSMITH_OIDC_SLUG")
  val cmd = oidcSlug match {
    case Some(slug) => Seq("cloudsmith", "tokens", "get", "--oidc-slug", slug)
    case None => Seq("cloudsmith", "tokens", "get")
  }
  
  Try(cmd.!!.trim).getOrElse {
    sys.error("Failed to get Cloudsmith token")
  }
}

credentials += Credentials(
  "Cloudsmith",
  "maven.cloudsmith.io",
  "token",
  getCloudsmithToken
)
```

**Usage**:
```bash
export CLOUDSMITH_OIDC_SLUG=my-org
sbt publish
```

This approach dynamically fetches tokens on each sbt invocation, so tokens never become stale.

---

### ✅ npm (JavaScript/Node.js)

**Support**: Yes - .npmrc with wrapper script or environment variables

npm supports authentication via `.npmrc` configuration files and environment variables.

**Recommended Approach** - Wrapper Script (see `examples/npm/`):

```bash
#!/bin/bash
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
npm config set //npm.cloudsmith.io/:_authToken "$TOKEN"
npm "$@"
```

**Usage**:
```bash
chmod +x npm-with-cloudsmith.sh
export CLOUDSMITH_OIDC_SLUG=my-org
./npm-with-cloudsmith.sh install
```

---

### ✅ NuGet (.NET)

**Support**: Yes - Credential provider plugin

NuGet supports external credential providers through its plugin protocol.

**Implementation** (see `examples/nuget/`):

The credential provider plugin integrates with dotnet CLI, NuGet.exe, and MSBuild to provide automatic authentication.

**Installation**:
```bash
mkdir -p ~/.nuget/plugins/netcore/CredentialProvider.Cloudsmith
cp cloudsmith-nuget-credprovider ~/.nuget/plugins/netcore/CredentialProvider.Cloudsmith/
chmod +x ~/.nuget/plugins/netcore/CredentialProvider.Cloudsmith/cloudsmith-nuget-credprovider
```

---

### ✅ Dart/Pub

**Support**: Yes - dart pub token command

Dart's pub tool has built-in support for token-based authentication.

**Recommended Approach** (see `examples/dart/`):

```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
dart pub token add https://dart.cloudsmith.io/my-org/my-repo/ --env-var CLOUDSMITH_TOKEN
export CLOUDSMITH_TOKEN="$TOKEN"
dart pub get
```

---

### ✅ Terraform

**Support**: Yes - Credential helper protocol

Terraform has full support for external credential helpers.

**Implementation** (see `examples/terraform/`):

```hcl
# .terraformrc
credentials_helper "cloudsmith" {
  args = []
}
```

The `terraform-credentials-cloudsmith` helper automatically provides credentials for Cloudsmith Terraform registries.

---

### ✅ Swift Package Manager

**Support**: Yes - .netrc file

Swift Package Manager uses `.netrc` for authentication.

**Recommended Approach** (see `examples/swift/`):

```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
echo "machine swift.cloudsmith.io login token password $TOKEN" > ~/.netrc
chmod 600 ~/.netrc
```

**Note**: Tokens expire after ~12 hours; use the wrapper script for automatic refresh.

---

### ✅ Go Modules

**Support**: Yes - .netrc file

Go modules use `.netrc` for authentication with private proxies.

**Recommended Approach** (see `examples/go/`):

```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
echo "machine go.cloudsmith.io login token password $TOKEN" > ~/.netrc
chmod 600 ~/.netrc
export GOPRIVATE="go.cloudsmith.io/my-org/*"
```

**Note**: Tokens expire after ~12 hours; use the wrapper script for automatic refresh.

---

### ✅ CRAN (R)

**Support**: Yes - renv with custom headers

R's renv package supports custom HTTP headers for authentication.

**Implementation** (see `examples/cran/`):

```r
# cloudsmith-auth.R
options(
  renv.download.headers = function(url) {
    if (grepl("cloudsmith.io", url)) {
      token <- system("cloudsmith tokens get", intern = TRUE)
      return(c(Authorization = paste0("Bearer ", token)))
    }
  }
)
```

---

## Removed/Unsupported Package Managers

The following package managers have been removed from this guide because they don't provide adequate mechanisms for dynamic credential retrieval and tokens expire after 12 hours:

### ❌ Conda
- No credential helper support
- Only supports static credentials in `.netrc` or environment variables
- Tokens would need to be manually refreshed every 12 hours

### ❌ Hex (Elixir)
- No credential helper support
- Only supports environment variables for `HEX_API_KEY`
- Would require manual token refresh every 12 hours

### ❌ Bundler (Ruby)
- While Bundler can use environment variables, it doesn't support dynamic credential providers
- Bundle config requires static credentials that would expire
- No practical way to auto-refresh tokens

### ❌ CocoaPods (iOS/macOS)
- No external credential helper support
- Only supports `.netrc` for Git-based private repos
- CDN approach doesn't support authentication at all
- Limited to basic auth without dynamic token refresh

---

## Summary Table

| Package Manager | Method | Auto Token Refresh | Implementation |
|----------------|--------|-------------------|----------------|
| **Docker** | Credential helper | ✅ Yes | `docker-credential-cloudsmith` |
| **Python/pip** | Keyring backend | ✅ Yes | `cloudsmith_keyring.py` |
| **npm** | Wrapper script + .npmrc | ✅ Yes | `npm-with-cloudsmith.sh` |
| **NuGet** | Credential provider | ✅ Yes | `cloudsmith-nuget-credprovider` |
| **Dart** | dart pub token | ✅ Yes | `dart-pub-with-cloudsmith.sh` |
| **Maven** | Wrapper script | ✅ Yes | `mvn-with-cloudsmith.sh` |
| **Gradle** | Exec in build.gradle | ✅ Yes | `getCloudsmithToken()` |
| **Helm 3** | Docker credentials | ✅ Yes | Uses Docker helper |
| **Helm 2** | Wrapper script | ⚠️ Manual | Manual repo add with token |
| **Conan** | Hooks | ✅ Yes | `cloudsmith_auth.py` hook |
| **Composer** | Wrapper script | ✅ Yes | `composer-with-cloudsmith.sh` |
| **Cargo** | Credential provider | ✅ Yes | `cargo-credential-cloudsmith` |
| **sbt** | Credential resolver | ✅ Yes | Dynamic in `credentials.sbt` |
| **Terraform** | Credential helper | ✅ Yes | `terraform-credentials-cloudsmith` |
| **Swift** | .netrc script | ⚠️ Manual | `setup-swift-auth.sh` |
| **Go** | .netrc script | ⚠️ Manual | `setup-go-auth.sh` |
| **R/CRAN** | renv headers | ✅ Yes | `cloudsmith-auth.R` |
| **Conda** | ❌ Not supported | No | No dynamic mechanism |
| **Hex** | ❌ Not supported | No | No dynamic mechanism |
| **Bundler** | ❌ Not supported | No | No dynamic mechanism |
| **CocoaPods** | ❌ Not supported | No | No credential helper support |

✅ = Full support with automatic token refresh  
⚠️ = Requires manual refresh (tokens expire after 12 hours)  
❌ = Not supported due to lack of dynamic credential mechanisms

## Contributing

If you create credential helpers for other package managers or improve existing ones, please contribute them to this directory!
