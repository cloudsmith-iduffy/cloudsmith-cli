# Terraform Credential Helper for Cloudsmith

A complete credential helper for Terraform that integrates with `cloudsmith tokens get` to provide automatic authentication for Cloudsmith Terraform registries.

## Features

- ✅ Full Terraform credential helper protocol support
- ✅ Automatic token retrieval and caching
- ✅ Supports API key, SAML, and OIDC authentication
- ✅ Cross-platform (Windows, macOS, Linux)

## Installation

Copy the credential helper to your PATH:

**macOS/Linux:**
```bash
chmod +x terraform-credentials-cloudsmith
sudo cp terraform-credentials-cloudsmith /usr/local/bin/
```

**Windows:**
```powershell
Copy-Item terraform-credentials-cloudsmith.exe C:\Windows\System32\
```

## Configuration

### .terraformrc (macOS/Linux) or terraform.rc (Windows)

```hcl
credentials_helper "cloudsmith" {
  args = []
}
```

Or with OIDC slug:

```hcl
credentials_helper "cloudsmith" {
  args = ["--oidc-slug=my-org"]
}
```

### Environment Variables

```bash
export CLOUDSMITH_OIDC_SLUG=my-org  # For OIDC
# OR
export CLOUDSMITH_API_KEY=your-key  # For API key
```

## Usage

Once configured, Terraform automatically uses the credential helper:

```hcl
terraform {
  required_providers {
    custom = {
      source = "terraform.cloudsmith.io/my-org/my-provider"
      version = "1.0.0"
    }
  }
}
```

Run Terraform commands normally:

```bash
terraform init
terraform plan
terraform apply
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Terraform Init
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: terraform init
```

**GitLab CI:**
```yaml
terraform:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - terraform init
    - terraform apply -auto-approve
```

## How It Works

1. Terraform needs credentials for `terraform.cloudsmith.io`
2. Terraform invokes `terraform-credentials-cloudsmith get terraform.cloudsmith.io`
3. The helper calls `cloudsmith tokens get` (with `--oidc-slug` if configured)
4. The token is returned as JSON: `{"token": "..."}`
5. Terraform uses the token for authentication

## Troubleshooting

### Credential helper not found

Ensure the executable is:
- Named `terraform-credentials-cloudsmith`
- In your system PATH
- Executable (macOS/Linux): `chmod +x terraform-credentials-cloudsmith`

### Authentication fails

Test the helper manually:
```bash
terraform-credentials-cloudsmith get terraform.cloudsmith.io
```

Verify cloudsmith CLI works:
```bash
cloudsmith tokens get
```

### Debug mode

Enable Terraform logging:
```bash
export TF_LOG=DEBUG
terraform init
```

## References

- [Terraform Credentials Helpers Documentation](https://developer.hashicorp.com/terraform/internals/credentials-helpers)
- [Cloudsmith Terraform Documentation](https://help.cloudsmith.io/docs/terraform-modules)
