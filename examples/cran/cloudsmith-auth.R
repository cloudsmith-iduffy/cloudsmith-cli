# Cloudsmith Authentication for R
#
# This script configures automatic authentication for Cloudsmith R repositories
# using the cloudsmith CLI to fetch tokens dynamically.
#
# Usage: source("cloudsmith-auth.R") in your .Rprofile or renv/activate.R

# Function to get Cloudsmith token
get_cloudsmith_token <- function() {
  oidc_slug <- Sys.getenv("CLOUDSMITH_OIDC_SLUG", unset = "")
  
  cmd <- "cloudsmith tokens get"
  if (nzchar(oidc_slug)) {
    cmd <- paste(cmd, "--oidc-slug", oidc_slug)
  }
  
  tryCatch({
    token <- system(cmd, intern = TRUE, ignore.stderr = TRUE)
    if (length(token) == 0 || !nzchar(token)) {
      warning("Failed to get Cloudsmith token")
      return(NULL)
    }
    return(trimws(token))
  }, error = function(e) {
    warning("Error getting Cloudsmith token: ", e$message)
    return(NULL)
  })
}

# Configure repositories
local({
  # Set up Cloudsmith repository
  cloudsmith_repo <- Sys.getenv("CLOUDSMITH_R_REPO", 
                                 unset = "https://r.cloudsmith.io/my-org/my-repo/")
  
  project_repos <- c(
    CLOUDSMITH = cloudsmith_repo,
    CRAN = "https://cloud.r-project.org"
  )
  
  options(repos = project_repos)
  
  # Configure authentication headers for renv
  options(
    renv.download.headers = function(url) {
      if (grepl("cloudsmith.io", url)) {
        token <- get_cloudsmith_token()
        if (!is.null(token)) {
          return(c(Authorization = paste0("Bearer ", token)))
        }
      }
      return(NULL)
    }
  )
  
  # Configure authentication for pak
  if (requireNamespace("pak", quietly = TRUE)) {
    options(
      pkg.download_headers = function(url) {
        if (grepl("cloudsmith.io", url)) {
          token <- get_cloudsmith_token()
          if (!is.null(token)) {
            return(c(Authorization = paste0("Bearer ", token)))
          }
        }
        return(NULL)
      }
    )
  }
})

message("Cloudsmith authentication configured")
