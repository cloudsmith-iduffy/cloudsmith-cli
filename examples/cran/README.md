# CRAN/R Authentication for Cloudsmith

Configure R package management to authenticate with Cloudsmith R (CRAN-like) repositories using `cloudsmith tokens get`.

## Features

- ✅ Uses renv for dynamic authentication
- ✅ Automatic token retrieval via custom headers
- ✅ Supports API key, SAML, and OIDC authentication
- ✅ Works with install.packages(), renv, and pak

## Installation

Add to your project's `renv/activate.R` or `.Rprofile`:

```r
source("cloudsmith-auth.R")
```

## Configuration

### cloudsmith-auth.R

The provided `cloudsmith-auth.R` script configures authentication using environment variables and custom HTTP headers.

### Environment Variables

```bash
export CLOUDSMITH_OIDC_SLUG=my-org  # For OIDC
# OR
export CLOUDSMITH_API_KEY=your-key  # For API key
```

## Usage

### Install Packages

```r
# Install from Cloudsmith repository
install.packages("my_package")

# With renv
renv::install("my_package")

# With pak
pak::pkg_install("my_package")
```

### Project Setup

1. Copy `cloudsmith-auth.R` to your project
2. Source it in `.Rprofile`:

```r
# .Rprofile
source("cloudsmith-auth.R")
```

3. Configure repositories:

```r
options(repos = c(
  CLOUDSMITH = "https://r.cloudsmith.io/my-org/my-repo/",
  CRAN = "https://cloud.r-project.org"
))
```

### CI/CD Examples

**GitHub Actions:**
```yaml
- name: Install R dependencies
  env:
    CLOUDSMITH_OIDC_SLUG: my-org
  run: |
    Rscript -e 'source("cloudsmith-auth.R"); renv::restore()'
```

**GitLab CI:**
```yaml
dependencies:
  script:
    - export CLOUDSMITH_OIDC_SLUG=my-org
    - Rscript -e 'source("cloudsmith-auth.R"); renv::restore()'
```

## How It Works

1. `cloudsmith-auth.R` fetches a token using `cloudsmith tokens get`
2. The token is injected as an Authorization header for Cloudsmith URLs
3. R's HTTP client uses the header when fetching packages
4. Tokens are refreshed on each R session start

## Troubleshooting

### Test token retrieval

```r
system("cloudsmith tokens get")
```

### Check repository configuration

```r
getOption("repos")
```

### Verify authentication headers

```r
getOption("renv.download.headers")
```

## References

- [renv Documentation](https://rstudio.github.io/renv/)
- [pak Documentation](https://pak.r-lib.org/)
- [Cloudsmith R Documentation](https://help.cloudsmith.io/docs/r-repository)
