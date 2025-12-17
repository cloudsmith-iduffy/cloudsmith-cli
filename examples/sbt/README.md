# sbt Integration for Cloudsmith

sbt credential resolver for Cloudsmith Scala repositories.

## Installation

### Prerequisites

- sbt 1.x
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Configuration

### Option 1: Global Credentials File (Recommended)

Create or edit `~/.sbt/1.0/credentials.sbt`:

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

### Option 2: Project-specific Configuration

Add to your `build.sbt`:

```scala
import scala.sys.process._

def cloudsmithToken: String = {
  val oidcSlug = sys.env.get("CLOUDSMITH_OIDC_SLUG")
  val cmd = oidcSlug.fold(Seq("cloudsmith", "tokens", "get"))(
    slug => Seq("cloudsmith", "tokens", "get", "--oidc-slug", slug)
  )
  cmd.!!.trim
}

credentials += Credentials(
  "Cloudsmith",
  "maven.cloudsmith.io",
  "token",
  cloudsmithToken
)

resolvers += "Cloudsmith" at "https://maven.cloudsmith.io/my-org/my-repo/"
```

### Option 3: Static Credentials File

Create `~/.sbt/.credentials`:

```
realm=Cloudsmith
host=maven.cloudsmith.io
user=token
password=YOUR_TOKEN_HERE
```

Update before running sbt:
```bash
TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
cat > ~/.sbt/.credentials << EOF
realm=Cloudsmith
host=maven.cloudsmith.io
user=token
password=$TOKEN
EOF
```

Reference in `build.sbt`:
```scala
credentials += Credentials(Path.userHome / ".sbt" / ".credentials")
```

## Usage

### Resolving Dependencies

**build.sbt**:
```scala
resolvers += "Cloudsmith" at "https://maven.cloudsmith.io/my-org/my-repo/"

libraryDependencies += "com.example" %% "my-library" % "1.0.0"
```

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
sbt compile
```

### Publishing Artifacts

**build.sbt**:
```scala
ThisBuild / organization := "com.example"
ThisBuild / version := "1.0.0"

publishTo := Some("Cloudsmith" at "https://maven.cloudsmith.io/my-org/my-repo/")
```

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
sbt publish
```

## Environment Variables

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC
- `CLOUDSMITH_API_KEY`: API key (fallback)

## Troubleshooting

### "Failed to get Cloudsmith token"

Ensure Cloudsmith CLI is installed:
```bash
pip install cloudsmith-cli

# Test token retrieval
cloudsmith tokens get --oidc-slug my-org
```

### Credentials not being used

Check credential realm and host match:
```scala
// Must match exactly
credentials += Credentials(
  "Cloudsmith",           // realm
  "maven.cloudsmith.io",  // host (without https://)
  "token",                // user
  getCloudsmithToken      // password
)
```

### sbt caching issues

Clear sbt cache:
```bash
rm -rf ~/.sbt/.credentials
rm -rf ~/.ivy2/cache
sbt clean
sbt compile
```

## Reference

- [sbt Publishing](https://www.scala-sbt.org/1.x/docs/Publishing.html)
- [sbt Credentials](https://www.scala-sbt.org/1.x/docs/Publishing.html#Credentials)
- [Cloudsmith Maven Repositories](https://help.cloudsmith.io/docs/maven-repository)
