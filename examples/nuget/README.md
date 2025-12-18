# NuGet Credential Provider for Cloudsmith

A complete credential provider plugin for NuGet that integrates with `cloudsmith tokens get` to provide automatic authentication for Cloudsmith NuGet feeds.

## Features

- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Works with dotnet CLI, NuGet.exe, and MSBuild
- ✅ Automatic token caching and refresh
- ✅ Supports API key, SAML, and OIDC authentication
- ✅ Compatible with NuGet 4.8+ credential provider plugin protocol

## Installation

### Manual Installation

Copy the credential provider to the NuGet plugins directory:

**Windows:**
```powershell
mkdir -p ~\.nuget\plugins\netcore\CredentialProvider.Cloudsmith\
Copy-Item cloudsmith-nuget-credprovider.exe ~\.nuget\plugins\netcore\CredentialProvider.Cloudsmith\
```

**macOS/Linux:**
```bash
mkdir -p ~/.nuget/plugins/netcore/CredentialProvider.Cloudsmith
cp cloudsmith-nuget-credprovider ~/.nuget/plugins/netcore/CredentialProvider.Cloudsmith/
chmod +x ~/.nuget/plugins/netcore/CredentialProvider.Cloudsmith/cloudsmith-nuget-credprovider
```

## Configuration

### NuGet.Config

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="cloudsmith" value="https://nuget.cloudsmith.io/my-org/my-repo/v3/index.json" />
  </packageSources>
</configuration>
```

### Environment Variables

```bash
export CLOUDSMITH_OIDC_SLUG=my-org  # For OIDC authentication
# OR
export CLOUDSMITH_API_KEY=your-api-key  # For API key authentication
```

## Usage

```bash
# Restore packages (automatically authenticates)
dotnet restore

# Push package
dotnet nuget push MyPackage.1.0.0.nupkg --source cloudsmith
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Restore packages
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: dotnet restore
```

**GitLab CI:**
```yaml
restore:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - dotnet restore
```

## References

- [NuGet Credential Providers Documentation](https://learn.microsoft.com/en-us/nuget/reference/extensibility/nuget-cross-platform-plugins)
- [Cloudsmith NuGet Documentation](https://help.cloudsmith.io/docs/nuget-feed)
