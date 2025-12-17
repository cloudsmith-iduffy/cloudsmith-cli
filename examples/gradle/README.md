# Gradle Integration for Cloudsmith

Gradle integration for Cloudsmith using dynamic credential retrieval via `cloudsmith tokens get`.

## Installation

### Prerequisites

- Gradle 6.x or later
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Configuration

### Option 1: Inline Credential Function (Recommended)

Add the credential function directly to your `build.gradle.kts`:

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

### Option 2: Shared Script

Create a shared script file and apply it to multiple projects.

**cloudsmith-credentials.gradle.kts** (provided in this directory):
```kotlin
// Copy the content and apply to your build
apply(from = "path/to/cloudsmith-credentials.gradle.kts")
```

### Option 3: Environment Variable

Set the token as an environment variable:

```kotlin
repositories {
    maven {
        name = "Cloudsmith"
        url = uri("https://maven.cloudsmith.io/my-org/my-repo/")
        credentials {
            username = "token"
            password = System.getenv("CLOUDSMITH_TOKEN")
        }
    }
}
```

```bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
gradle build
```

### Option 4: Gradle Properties

Set credentials via gradle.properties:

**~/.gradle/gradle.properties**:
```properties
cloudsmithUsername=token
cloudsmithPassword=YOUR_TOKEN_HERE
```

**build.gradle.kts**:
```kotlin
repositories {
    maven {
        name = "Cloudsmith"
        url = uri("https://maven.cloudsmith.io/my-org/my-repo/")
        credentials {
            username = project.findProperty("cloudsmithUsername") as String? ?: "token"
            password = project.findProperty("cloudsmithPassword") as String? ?: ""
        }
    }
}
```

Update token before running Gradle:
```bash
# Update gradle.properties programmatically
echo "cloudsmithPassword=$(cloudsmith tokens get --oidc-slug my-org)" > ~/.gradle/gradle.properties.tmp
cat ~/.gradle/gradle.properties.tmp >> ~/.gradle/gradle.properties
rm ~/.gradle/gradle.properties.tmp

gradle publish
```

## Usage

### Consuming Dependencies

**build.gradle.kts**:
```kotlin
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

dependencies {
    implementation("com.example:my-library:1.0.0")
}
```

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
gradle build
```

### Publishing Artifacts

**build.gradle.kts**:
```kotlin
plugins {
    `maven-publish`
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
            groupId = "com.example"
            artifactId = "my-library"
            version = "1.0.0"
        }
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
}
```

```bash
export CLOUDSMITH_OIDC_SLUG=my-org
gradle publish
```

## Environment Variables

- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC authentication
- `CLOUDSMITH_TOKEN`: Pre-fetched token (alternative approach)
- `CLOUDSMITH_API_KEY`: API key (fallback)

## Troubleshooting

### "Could not resolve"

Ensure credentials are configured correctly:
```bash
# Test credential retrieval
cloudsmith tokens get --oidc-slug my-org

# Run Gradle with info logging
gradle build --info
```

### "Credentials required"

Verify the credential function is working:
```bash
# Test the function standalone
export CLOUDSMITH_OIDC_SLUG=my-org
gradle --quiet -b test.gradle.kts help

# test.gradle.kts:
# println(getCloudsmithToken())
```

### Gradle Daemon Issues

The Gradle daemon may cache environment variables. Restart it:
```bash
gradle --stop
gradle build
```

## Best Practices

1. **Use OIDC in CI/CD**: Set `CLOUDSMITH_OIDC_SLUG` for automatic token exchange
2. **Cache credentials wisely**: Don't cache tokens for too long (they may expire)
3. **Use configuration cache carefully**: Token retrieval happens at configuration time
4. **Parallel builds**: Each build will fetch its own token

## Reference

- [Gradle Dependency Management](https://docs.gradle.org/current/userguide/dependency_management.html)
- [Gradle Publishing](https://docs.gradle.org/current/userguide/publishing_maven.html)
- [Cloudsmith Maven Repositories](https://help.cloudsmith.io/docs/maven-repository)
