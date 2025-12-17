"""Tests for OIDC functionality."""

import os
from unittest.mock import MagicMock, mock_open, patch

from cloudsmith_cli.cli.oidc import (
    detect_oidc_provider,
    exchange_oidc_token,
    get_oidc_token,
)


class TestDetectOIDCProvider:
    """Test suite for CI environment detection."""

    def test_detect_github_actions(self):
        """Test detection of GitHub Actions environment."""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            provider, token_var = detect_oidc_provider()
            assert provider == "github"
            assert token_var == "ACTIONS_ID_TOKEN_REQUEST_TOKEN"

    def test_detect_gitlab_ci(self):
        """Test detection of GitLab CI environment."""
        with patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True):
            provider, token_var = detect_oidc_provider()
            assert provider == "gitlab"
            assert token_var == "CI_JOB_JWT_V2"

    def test_detect_circleci(self):
        """Test detection of CircleCI environment."""
        with patch.dict(os.environ, {"CIRCLECI": "true"}, clear=True):
            provider, token_var = detect_oidc_provider()
            assert provider == "circleci"
            assert token_var == "CIRCLE_OIDC_TOKEN"

    def test_detect_aws_codebuild(self):
        """Test detection of AWS CodeBuild environment."""
        with patch.dict(
            os.environ, {"CODEBUILD_BUILD_ID": "some-build-id"}, clear=True
        ):
            provider, token_var = detect_oidc_provider()
            assert provider == "aws"
            assert token_var == "AWS_WEB_IDENTITY_TOKEN_FILE"

    def test_detect_azure_pipelines(self):
        """Test detection of Azure Pipelines environment."""
        with patch.dict(os.environ, {"AZURE_PIPELINES": "true"}, clear=True):
            provider, token_var = detect_oidc_provider()
            assert provider == "azure"
            assert token_var == "SYSTEM_OIDCTOKEN"

    def test_detect_no_ci(self):
        """Test that no CI is detected in a regular environment."""
        with patch.dict(os.environ, {}, clear=True):
            provider, token_var = detect_oidc_provider()
            assert provider is None
            assert token_var is None


class TestGetOIDCToken:
    """Test suite for getting OIDC tokens from CI environments."""

    def test_get_github_token_success(self):
        """Test successfully getting a GitHub Actions OIDC token."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_ACTIONS": "true",
                "ACTIONS_ID_TOKEN_REQUEST_URL": "https://api.github.com/token",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request_token_123",
            },
        ), patch("cloudsmith_cli.cli.oidc.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"value": "github_token_123"}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            token = get_oidc_token()
            assert token == "github_token_123"

    def test_get_gitlab_token(self):
        """Test getting a GitLab CI OIDC token."""
        with patch.dict(
            os.environ,
            {"GITLAB_CI": "true", "CI_JOB_JWT_V2": "gitlab_token_456"},
            clear=True,
        ):
            token = get_oidc_token()
            assert token == "gitlab_token_456"

    def test_get_circleci_token(self):
        """Test getting a CircleCI OIDC token."""
        with patch.dict(
            os.environ,
            {"CIRCLECI": "true", "CIRCLE_OIDC_TOKEN": "circleci_token_789"},
            clear=True,
        ):
            token = get_oidc_token()
            assert token == "circleci_token_789"

    def test_get_aws_token_from_file(self):
        """Test getting an AWS OIDC token from a file."""
        with patch.dict(
            os.environ,
            {
                "CODEBUILD_BUILD_ID": "build-123",
                "AWS_WEB_IDENTITY_TOKEN_FILE": "/tmp/token.txt",
            },
            clear=True,
        ), patch("builtins.open", mock_open(read_data="aws_token_abc")), patch(
            "os.path.exists", return_value=True
        ):
            token = get_oidc_token()
            assert token == "aws_token_abc"

    def test_get_azure_token(self):
        """Test getting an Azure Pipelines OIDC token."""
        with patch.dict(
            os.environ,
            {"AZURE_PIPELINES": "true", "SYSTEM_OIDCTOKEN": "azure_token_xyz"},
            clear=True,
        ):
            token = get_oidc_token()
            assert token == "azure_token_xyz"

    def test_get_token_no_ci(self):
        """Test that None is returned when not in a CI environment."""
        with patch.dict(os.environ, {}, clear=True):
            token = get_oidc_token()
            assert token is None


class TestExchangeOIDCToken:
    """Test suite for OIDC token exchange."""

    def test_exchange_token_success(self):
        """Test successful OIDC token exchange."""
        with patch("cloudsmith_cli.cli.oidc.requests.Session") as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = {"token": "cloudsmith_token_123"}
            mock_response.raise_for_status = MagicMock()
            mock_session.return_value.post.return_value = mock_response

            token = exchange_oidc_token(
                "https://api.cloudsmith.io", "oidc_token_456", "my-org"
            )
            assert token == "cloudsmith_token_123"

    def test_exchange_token_with_access_token(self):
        """Test OIDC token exchange when response uses 'access_token' key."""
        with patch("cloudsmith_cli.cli.oidc.requests.Session") as mock_session:
            mock_response = MagicMock()
            mock_response.json.return_value = {"access_token": "cloudsmith_token_789"}
            mock_response.raise_for_status = MagicMock()
            mock_session.return_value.post.return_value = mock_response

            token = exchange_oidc_token(
                "https://api.cloudsmith.io", "oidc_token_456", "my-org"
            )
            assert token == "cloudsmith_token_789"
