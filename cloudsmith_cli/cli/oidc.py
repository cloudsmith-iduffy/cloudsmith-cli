"""CLI - OIDC Token Exchange utilities."""

import json
import os
import time
from datetime import datetime, timedelta

import requests

from ..core.api.exceptions import ApiException

# In-memory cache for within-process token reuse
# Persistent cache uses keyring (like SAML tokens)
_MEMORY_CACHE = {}


def detect_oidc_provider():
    """
    Detect which OIDC provider credentials are available.

    Returns:
        str: provider name or None if no OIDC credentials available
    """
    # GitHub Actions
    if os.getenv("GITHUB_ACTIONS") == "true":
        return "github"

    # GitLab CI
    if os.getenv("GITLAB_CI") == "true":
        return "gitlab"

    # CircleCI
    if os.getenv("CIRCLECI") == "true":
        return "circleci"

    # AWS - Check for credentials that indicate AWS environment
    # Could be: AWS_REGION + AWS credentials, or successful STS caller identity
    try:
        import boto3  # pylint: disable=import-outside-toplevel
        # Try to get caller identity - if this works, we have valid AWS credentials
        sts = boto3.client("sts")
        sts.get_caller_identity()
        return "aws"
    except Exception:  # pylint: disable=broad-except
        pass

    # Azure Pipelines
    # More complex - requires OIDC request URI
    # https://cloudsmith.com/changelog/native-oidc-authentication-for-azure-devops
    if os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI") and os.getenv(
        "SYSTEM_OIDCREQUESTURI"
    ):
        return "azure"

    # Bitbucket Pipelines
    if os.getenv("BITBUCKET_PIPELINE_UUID"):
        return "bitbucket"

    # Jenkins with OIDC plugin
    if os.getenv("JENKINS_URL") and os.getenv("OIDC_TOKEN"):
        return "jenkins"

    return None


def get_github_token():
    """Get OIDC token from GitHub Actions."""
    token_url = os.getenv("ACTIONS_ID_TOKEN_REQUEST_URL")
    request_token = os.getenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN")

    if not token_url or not request_token:
        return None

    try:
        headers = {"Authorization": f"Bearer {request_token}"}
        response = requests.get(token_url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("value")
    except (requests.RequestException, KeyError):
        return None


def get_gitlab_token():
    """Get OIDC token from GitLab CI."""
    return os.getenv("CI_JOB_JWT_V2")


def get_circleci_token():
    """Get OIDC token from CircleCI."""
    return os.getenv("CIRCLE_OIDC_TOKEN")


def get_aws_token():
    """
    Get OIDC token from AWS using External Identity Federation.
    
    Uses AWS STS get_web_identity_token as per:
    https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound.html
    """
    try:
        import boto3  # pylint: disable=import-outside-toplevel
        
        sts_client = boto3.client('sts')
        response = sts_client.get_web_identity_token(
            Audience=['cloudsmith.io'],
            SigningAlgorithm='RS256',  # or 'ES384'
            DurationSeconds=900  # 15 minutes
        )
        return response['WebIdentityToken']
    except Exception:  # pylint: disable=broad-except
        # Fall back to environment variable or file-based token
        token_file = os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE")
        if token_file and os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except (IOError, OSError):
                return None
        return None


def get_azure_token():
    """Get OIDC token from Azure Pipelines."""
    oidc_request_uri = os.getenv("SYSTEM_OIDCREQUESTURI")
    access_token = os.getenv("SYSTEM_ACCESSTOKEN")

    if not oidc_request_uri or not access_token:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Content-Length": "0",
        }
        response = requests.post(
            f"{oidc_request_uri}?api-version=7.1",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("oidcToken")
    except (requests.RequestException, KeyError):
        return None


def get_bitbucket_token():
    """Get OIDC token from Bitbucket Pipelines."""
    return os.getenv("BITBUCKET_STEP_OIDC_TOKEN")


def get_jenkins_token():
    """Get OIDC token from Jenkins."""
    return os.getenv("OIDC_TOKEN")


def get_oidc_token():
    """
    Get the OIDC token from the current environment.

    Returns:
        str: The OIDC token, or None if not available
    """
    provider = detect_oidc_provider()

    if not provider:
        return None

    # Call the appropriate provider function
    provider_functions = {
        "github": get_github_token,
        "gitlab": get_gitlab_token,
        "circleci": get_circleci_token,
        "aws": get_aws_token,
        "azure": get_azure_token,
        "bitbucket": get_bitbucket_token,
        "jenkins": get_jenkins_token,
    }

    get_token_func = provider_functions.get(provider)
    if get_token_func:
        return get_token_func()

    return None


def exchange_oidc_token(api_host, oidc_token, service_slug, session=None):
    """
    Exchange an OIDC token for a Cloudsmith API token with persistent caching.

    Tokens are cached in keyring (like SAML tokens) for persistence across CLI invocations.

    Args:
        api_host: The Cloudsmith API host
        oidc_token: The OIDC token to exchange
        service_slug: The service slug (organization slug) for the OIDC provider
        session: Optional requests session to use

    Returns:
        str: The Cloudsmith API token

    Raises:
        ApiException: If the exchange fails

    Example:
        The endpoint format is: {api_host}/openid/{org}/
        The request payload should contain:
        {
            "oidc_token": "<token>",
            "service_slug": "<slug>"
        }
    """
    cache_key = f"oidc_{api_host}_{service_slug}"
    
    # Check in-memory cache first (fast path)
    if cache_key in _MEMORY_CACHE:
        cached_token, expiry = _MEMORY_CACHE[cache_key]
        if time.time() < expiry:
            return cached_token
        # Expired, remove from cache
        del _MEMORY_CACHE[cache_key]
    
    # Check persistent cache in keyring
    try:
        # Use keyring's internal API
        import getpass
        from keyring.errors import KeyringError
        import keyring as kr  # rename to avoid conflict with module name
        
        username = getpass.getuser()
        keyring_key = f"cloudsmith_cli-{cache_key}"
        cached_data = kr.get_password(keyring_key, username)
        
        if cached_data:
            cached_json = json.loads(cached_data)
            cached_token = cached_json.get("token")
            expiry = cached_json.get("expiry", 0)
            
            if time.time() < expiry and cached_token:
                # Update in-memory cache
                _MEMORY_CACHE[cache_key] = (cached_token, expiry)
                return cached_token
            # Expired, remove from keyring
            try:
                kr.delete_password(keyring_key, username)
            except KeyringError:
                pass
    except Exception:  # pylint: disable=broad-except
        # Keyring errors are non-fatal
        pass

    if session is None:
        session = requests.Session()

    # The endpoint for OIDC token exchange
    # Format: https://api.cloudsmith.io/openid/{org}/
    exchange_url = f"{api_host}/openid/{service_slug}/"

    data = {"oidc_token": oidc_token, "service_slug": service_slug}

    try:
        response = session.post(exchange_url, json=data, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        
        token = response_data.get("token") or response_data.get("access_token")
        
        # Cache the token (in-memory and persistent)
        # Default to 12 hours if no expiry provided, minus 5 minutes for safety
        expiry_seconds = response_data.get("expires_in", 12 * 3600) - 300
        expiry_timestamp = time.time() + expiry_seconds
        
        # Store in memory
        _MEMORY_CACHE[cache_key] = (token, expiry_timestamp)
        
        # Store in keyring for persistence across CLI invocations
        try:
            import getpass
            import keyring as kr
            
            cache_data = json.dumps({"token": token, "expiry": expiry_timestamp})
            username = getpass.getuser()
            keyring_key = f"cloudsmith_cli-{cache_key}"
            kr.set_password(keyring_key, username, cache_data)
        except Exception:  # pylint: disable=broad-except
            # Keyring errors are non-fatal
            pass
        
        return token
    except requests.RequestException as exc:
        if hasattr(exc, "response") and exc.response is not None:
            raise ApiException(
                exc.response.status_code,
                headers=exc.response.headers,
                body=exc.response.content,
            )
        raise ApiException(500, body=str(exc))
