"""CLI - OIDC Token Exchange utilities."""

import os

import requests

from ..core.api.exceptions import ApiException


def detect_ci_environment():
    """
    Detect which CI/CD environment we're running in.

    Returns:
        tuple: (provider_name, token_env_var) or (None, None) if not in CI
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

    # AWS CodeBuild
    if os.getenv("CODEBUILD_BUILD_ID"):
        return ("aws", "AWS_WEB_IDENTITY_TOKEN_FILE")

    # Azure Pipelines
    # Note: SYSTEM_OIDCTOKEN is only available in Azure Pipelines with OIDC enabled
    if os.getenv("AZURE_PIPELINES") == "true" or os.getenv(
        "SYSTEM_TEAMFOUNDATIONCOLLECTIONURI"
    ):
        return ("azure", "SYSTEM_OIDCTOKEN")

    return (None, None)


def get_ci_oidc_token():
    """
    Get the OIDC token from the current CI/CD environment.

    Returns:
        str: The OIDC token, or None if not available
    """
    # pylint: disable=too-many-return-statements
    provider, token_env_var = detect_ci_environment()

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

    # AWS uses a file path
    if provider == "aws":
        token_file = os.getenv(token_env_var)
        if token_file and os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except (IOError, OSError):
                return None
        return None

    # For other providers, the token is directly in the environment variable
    return os.getenv(token_env_var)


def exchange_oidc_token(api_host, oidc_token, provider, session=None):
    """
    Exchange an OIDC token from a CI/CD provider for a Cloudsmith token.

    Args:
        api_host: The Cloudsmith API host
        oidc_token: The OIDC token from the CI/CD provider
        provider: The provider name (github, gitlab, circleci, aws, azure)
        session: Optional requests session to use

    Returns:
        str: The Cloudsmith access token

    Raises:
        ApiException: If the exchange fails

    Note:
        The OIDC token exchange endpoint and payload format should be verified
        against the Cloudsmith API documentation. This implementation follows
        a standard pattern for OIDC token exchange. The actual endpoint may vary
        depending on the Cloudsmith API version and configuration.

        TODO: Verify the exact API endpoint format with Cloudsmith API documentation.
    """
    if session is None:
        session = requests.Session()

    # The endpoint for OIDC token exchange
    # This follows a common pattern for OIDC token exchange in cloud services
    exchange_url = f"{api_host}/openid/{provider}/token-exchange/"

    data = {"token": oidc_token, "provider": provider}

    try:
        response = session.post(exchange_url, json=data, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("token") or response_data.get("access_token")
    except requests.RequestException as exc:
        if hasattr(exc, "response") and exc.response is not None:
            raise ApiException(
                exc.response.status_code,
                headers=exc.response.headers,
                body=exc.response.content,
            )
        raise ApiException(500, body=str(exc))
