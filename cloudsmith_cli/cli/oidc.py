"""CLI - OIDC Token Exchange utilities."""

import json
import os
import time
from datetime import datetime, timedelta

import requests

from ..core.api.exceptions import ApiException

# Token cache: {(api_host, service_slug): (token, expiry_timestamp)}
_TOKEN_CACHE = {}


def detect_oidc_provider():
    """
    Detect which OIDC provider credentials are available.

    Returns:
        tuple: (provider_name, token_env_var) or (None, None) if no OIDC token available
    """
    # GitHub Actions
    if os.getenv("GITHUB_ACTIONS") == "true":
        return ("github", "ACTIONS_ID_TOKEN_REQUEST_TOKEN")

    # GitLab CI
    if os.getenv("GITLAB_CI") == "true":
        return ("gitlab", "CI_JOB_JWT_V2")

    # CircleCI
    if os.getenv("CIRCLECI") == "true":
        return ("circleci", "CIRCLE_OIDC_TOKEN")

    # AWS - External Identity Federation
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_outbound.html
    if os.getenv("AWS_REGION"):
        return ("aws", "AWS_REGION")

    # Azure Pipelines
    # More complex - requires OIDC request URI
    # https://cloudsmith.com/changelog/native-oidc-authentication-for-azure-devops
    if os.getenv("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI") and os.getenv(
        "SYSTEM_OIDCREQUESTURI"
    ):
        return ("azure", "SYSTEM_OIDCREQUESTURI")

    # Bitbucket Pipelines
    if os.getenv("BITBUCKET_PIPELINE_UUID"):
        return ("bitbucket", "BITBUCKET_STEP_OIDC_TOKEN")

    # Jenkins with OIDC plugin
    if os.getenv("JENKINS_URL") and os.getenv("OIDC_TOKEN"):
        return ("jenkins", "OIDC_TOKEN")

    return (None, None)


def get_oidc_token():
    """
    Get the OIDC token from the current environment.

    Returns:
        str: The OIDC token, or None if not available
    """
    # pylint: disable=too-many-return-statements
    provider, token_env_var = detect_oidc_provider()

    if not provider:
        return None

    # GitHub Actions requires a special request to get the token
    if provider == "github":
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

    # AWS External Identity Federation
    # Uses AWS STS get-caller-identity to get OIDC token
    if provider == "aws":
        try:
            import boto3  # pylint: disable=import-outside-toplevel
            
            # Use STS to get the caller identity which includes OIDC info
            sts = boto3.client("sts")
            # Get web identity token if available
            token = sts.assume_role_with_web_identity(
                RoleArn=os.getenv("AWS_ROLE_ARN"),
                RoleSessionName="cloudsmith-cli-session",
                WebIdentityToken=os.getenv("AWS_WEB_IDENTITY_TOKEN", ""),
            )
            return token.get("Credentials", {}).get("SessionToken")
        except Exception:  # pylint: disable=broad-except
            # Fall back to checking for web identity token file
            token_file = os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE")
            if token_file and os.path.exists(token_file):
                try:
                    with open(token_file, "r", encoding="utf-8") as f:
                        return f.read().strip()
                except (IOError, OSError):
                    return None
            return None

    # Azure Pipelines requires a request to OIDC endpoint
    if provider == "azure":
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

    # For other providers, the token is directly in the environment variable
    return os.getenv(token_env_var)


def exchange_oidc_token(api_host, oidc_token, service_slug, session=None):
    """
    Exchange an OIDC token for a Cloudsmith API token with caching.

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
    # Check cache first
    cache_key = (api_host, service_slug)
    if cache_key in _TOKEN_CACHE:
        cached_token, expiry = _TOKEN_CACHE[cache_key]
        if time.time() < expiry:
            return cached_token
        # Expired, remove from cache
        del _TOKEN_CACHE[cache_key]

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
        
        # Cache the token
        # Default to 12 hours if no expiry provided, minus 5 minutes for safety
        expiry_seconds = response_data.get("expires_in", 12 * 3600) - 300
        expiry_timestamp = time.time() + expiry_seconds
        _TOKEN_CACHE[cache_key] = (token, expiry_timestamp)
        
        return token
    except requests.RequestException as exc:
        if hasattr(exc, "response") and exc.response is not None:
            raise ApiException(
                exc.response.status_code,
                headers=exc.response.headers,
                body=exc.response.content,
            )
        raise ApiException(500, body=str(exc))
