"""
Cloudsmith Authentication Hook for Conan

This hook automatically retrieves Cloudsmith authentication tokens
using the `cloudsmith tokens get` command.

Installation:
    1. Copy this file to ~/.conan/hooks/cloudsmith_auth.py
    2. Enable hooks in Conan (enabled by default in Conan 1.21+)

Environment Variables:
    CLOUDSMITH_OIDC_SLUG: Organization slug for OIDC authentication (optional)
    CLOUDSMITH_API_KEY: API key for authentication (optional)
"""

import os
import subprocess


def get_cloudsmith_token():
    """Get authentication token from Cloudsmith CLI."""
    cmd = ["cloudsmith", "tokens", "get"]
    
    oidc_slug = os.environ.get("CLOUDSMITH_OIDC_SLUG")
    if oidc_slug:
        cmd.extend(["--oidc-slug", oidc_slug])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        return None


def pre_download(output, reference, remote, **kwargs):
    """
    Hook called before downloading packages.
    
    Automatically authenticates with Cloudsmith remotes.
    """
    remote_url = kwargs.get("url", "")
    
    # Check if this is a Cloudsmith remote
    if "cloudsmith.io" in str(remote) or "cloudsmith.io" in str(remote_url):
        output.info("Authenticating with Cloudsmith...")
        
        token = get_cloudsmith_token()
        if token:
            output.info("Successfully retrieved Cloudsmith token")
            # Store token for this session
            os.environ["CONAN_LOGIN_USERNAME"] = "token"
            os.environ["CONAN_PASSWORD"] = token
        else:
            output.warn("Could not retrieve Cloudsmith token. Install cloudsmith-cli: pip install cloudsmith-cli")


def pre_upload(output, reference, remote, **kwargs):
    """
    Hook called before uploading packages.
    
    Automatically authenticates with Cloudsmith remotes.
    """
    remote_url = kwargs.get("url", "")
    
    # Check if this is a Cloudsmith remote
    if "cloudsmith.io" in str(remote) or "cloudsmith.io" in str(remote_url):
        output.info("Authenticating with Cloudsmith...")
        
        token = get_cloudsmith_token()
        if token:
            output.info("Successfully retrieved Cloudsmith token")
            # Store token for this session
            os.environ["CONAN_LOGIN_USERNAME"] = "token"
            os.environ["CONAN_PASSWORD"] = token
        else:
            output.warn("Could not retrieve Cloudsmith token. Install cloudsmith-cli: pip install cloudsmith-cli")
