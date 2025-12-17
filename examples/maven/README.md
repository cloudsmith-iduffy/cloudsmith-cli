# Maven Credential Helper for Cloudsmith

Maven integration for Cloudsmith using dynamic credential retrieval via `cloudsmith tokens get`.

## Installation

### Prerequisites

- Maven 3.x or later
- Cloudsmith CLI: `pip install cloudsmith-cli`

### Setup

1. Make the credential script executable:
```bash
chmod +x cloudsmith-maven-creds
sudo cp cloudsmith-maven-creds /usr/local/bin/
```

## Configuration

### Option 1: Environment Variable (Recommended)

Configure Maven to use credentials from environment variables in your `~/.m2/settings.xml`:

```xml
<settings>
  <servers>
    <server>
      <id>cloudsmith</id>
      <username>token</username>
      <password>${env.CLOUDSMITH_TOKEN}</password>
    </server>
  </servers>
  
  <profiles>
    <profile>
      <id>cloudsmith</id>
      <repositories>
        <repository>
          <id>cloudsmith</id>
          <url>https://maven.cloudsmith.io/my-org/my-repo/</url>
        </repository>
      </repositories>
    </profile>
  </profiles>
  
  <activeProfiles>
    <activeProfile>cloudsmith</activeProfile>
  </activeProfiles>
</settings>
```

Then set the token before running Maven:
```bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
mvn deploy
```

### Option 2: Dynamic Credential Script

Use a wrapper script that sets credentials dynamically:

**maven-with-cloudsmith.sh**:
```bash
#!/bin/bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
mvn "$@"
```

Make it executable:
```bash
chmod +x maven-with-cloudsmith.sh
./maven-with-cloudsmith.sh deploy
```

### Option 3: Settings Encryption with Script

For settings encryption, create a master password and use it with the credential script:

```bash
# Generate master password
mvn --encrypt-master-password $(cloudsmith-maven-creds)

# Encrypt server password
mvn --encrypt-password $(cloudsmith-maven-creds)
```

## Usage

### Publishing to Cloudsmith

**pom.xml**:
```xml
<project>
  <distributionManagement>
    <repository>
      <id>cloudsmith</id>
      <url>https://maven.cloudsmith.io/my-org/my-repo/</url>
    </repository>
  </distributionManagement>
</project>
```

**Deploy**:
```bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
mvn deploy
```

### Using Cloudsmith as Dependency Source

**pom.xml**:
```xml
<project>
  <repositories>
    <repository>
      <id>cloudsmith</id>
      <url>https://maven.cloudsmith.io/my-org/my-repo/</url>
    </repository>
  </repositories>
</project>
```

**Install dependencies**:
```bash
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
mvn install
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Maven Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Install Cloudsmith CLI
        run: pip install cloudsmith-cli
      
      - name: Set Cloudsmith token
        run: echo "CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)" >> $GITHUB_ENV
      
      - name: Build and deploy
        run: mvn deploy
```

### GitLab CI

```yaml
build:
  image: maven:3-openjdk-17
  before_script:
    - pip install cloudsmith-cli
    - export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)
  script:
    - mvn deploy
```

## Environment Variables

- `CLOUDSMITH_TOKEN`: The authentication token (set dynamically)
- `CLOUDSMITH_OIDC_SLUG`: Organization slug for OIDC authentication
- `CLOUDSMITH_API_KEY`: API key (alternative to OIDC)

## Troubleshooting

### "Could not find artifact"

Ensure your repository is configured correctly and credentials are set:
```bash
# Test credential retrieval
cloudsmith tokens get --oidc-slug my-org

# Verify environment variable is set
echo $CLOUDSMITH_TOKEN
```

### "Unauthorized"

Check that your token is valid:
```bash
# Get fresh token
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get --oidc-slug my-org)

# Retry Maven command
mvn deploy
```

## Reference

- [Maven Settings Reference](https://maven.apache.org/settings.html)
- [Maven Password Encryption](https://maven.apache.org/guides/mini/guide-encryption.html)
- [Cloudsmith Maven Repositories](https://help.cloudsmith.io/docs/maven-repository)
