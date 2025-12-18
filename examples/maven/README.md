# Maven Credential Helper for Cloudsmith

Maven integration for Cloudsmith using dynamic credential retrieval via `cloudsmith tokens get`.

## Installation

### Prerequisites

- Maven 3.2.1 or later
- Cloudsmith CLI: `pip install cloudsmith-cli`

## Configuration

### Option 1: Maven Extension (Recommended)

Maven 3.2.1+ supports extensions that can inject credentials dynamically. Create a custom extension or use the shell execution approach:

**pom.xml** with build extension:
```xml
<project>
  <build>
    <extensions>
      <extension>
        <groupId>org.apache.maven.wagon</groupId>
        <artifactId>wagon-http</artifactId>
        <version>3.5.3</version>
      </extension>
    </extensions>
  </build>
</project>
```

**~/.m2/settings.xml**:
```xml
<settings>
  <servers>
    <server>
      <id>cloudsmith</id>
      <configuration>
        <httpHeaders>
          <property>
            <name>Authorization</name>
            <!-- This gets evaluated at runtime -->
            <value>Bearer ${env.CLOUDSMITH_TOKEN}</value>
          </property>
        </httpHeaders>
      </configuration>
    </server>
  </servers>
</settings>
```

Then use a wrapper script to set the token:
```bash
#!/bin/bash
# mvn-cloudsmith.sh
export CLOUDSMITH_TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})
mvn "$@"
```

Usage:
```bash
chmod +x mvn-cloudsmith.sh
./mvn-cloudsmith.sh clean install
./mvn-cloudsmith.sh deploy
```

### Option 2: Maven Plugin with Exec

Use the exec-maven-plugin to fetch credentials before each build:

**pom.xml**:
```xml
<project>
  <build>
    <plugins>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.1.0</version>
        <executions>
          <execution>
            <id>fetch-cloudsmith-token</id>
            <phase>initialize</phase>
            <goals>
              <goal>exec</goal>
            </goals>
            <configuration>
              <executable>sh</executable>
              <arguments>
                <argument>-c</argument>
                <argument>cloudsmith tokens get ${env.CLOUDSMITH_OIDC_SLUG}</argument>
              </arguments>
              <outputProperty>cloudsmith.token</outputProperty>
            </configuration>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
```

**~/.m2/settings.xml**:
```xml
<settings>
  <servers>
    <server>
      <id>cloudsmith</id>
      <username>token</username>
      <password>${cloudsmith.token}</password>
    </server>
  </servers>
</settings>
```

Usage:
```bash
export CLOUDSMITH_OIDC_SLUG=my-org
mvn deploy
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
