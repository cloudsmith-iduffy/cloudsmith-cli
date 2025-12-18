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
            provider = detect_oidc_provider()
            assert provider == "github"

    def test_detect_gitlab_ci(self):
        """Test detection of GitLab CI environment."""
        with patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True):
            provider = detect_oidc_provider()
            assert provider == "gitlab"

    def test_detect_circleci(self):
        """Test detection of CircleCI environment."""
        with patch.dict(os.environ, {"CIRCLECI": "true"}, clear=True):
            provider = detect_oidc_provider()
            assert provider == "circleci"

    def test_detect_aws_with_credentials(self):
        """Test detection of AWS environment with valid credentials."""
        with patch("boto3.client") as mock_boto_client:
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
            mock_boto_client.return_value = mock_sts
            
            provider = detect_oidc_provider()
            assert provider == "aws"

    def test_detect_azure_pipelines(self):
        """Test detection of Azure Pipelines environment."""
        with patch.dict(
            os.environ,
            {
                "SYSTEM_TEAMFOUNDATIONCOLLECTIONURI": "https://dev.azure.com/org",
                "SYSTEM_OIDCREQUESTURI": "https://dev.azure.com/org/_apis/oidc"
            },
            clear=True
        ):
            provider = detect_oidc_provider()
            assert provider == "azure"

    def test_detect_no_provider(self):
        """Test that no provider is detected in a regular environment."""
        with patch.dict(os.environ, {}, clear=True), patch("boto3.client", side_effect=Exception("No boto3")):
            provider = detect_oidc_provider()
            assert provider is None


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

    def test_get_aws_token_via_sts(self):
        """Test getting an AWS OIDC token via STS get_web_identity_token."""
        with patch("boto3.client") as mock_boto_client:
            mock_sts = MagicMock()
            mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
            mock_sts.get_web_identity_token.return_value = {"WebIdentityToken": "aws_sts_token_123"}
            mock_boto_client.return_value = mock_sts
            
            token = get_oidc_token()
            assert token == "aws_sts_token_123"

    def test_get_azure_token(self):
        """Test getting an Azure Pipelines OIDC token."""
        with patch.dict(
            os.environ,
            {
                "SYSTEM_TEAMFOUNDATIONCOLLECTIONURI": "https://dev.azure.com/org",
                "SYSTEM_OIDCREQUESTURI": "https://dev.azure.com/org/_apis/oidc",
                "SYSTEM_ACCESSTOKEN": "azure_access_token_xyz",
            },
            clear=True,
        ), patch("cloudsmith_cli.cli.oidc.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"oidcToken": "azure_oidc_token_xyz"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            token = get_oidc_token()
            assert token == "azure_oidc_token_xyz"

    def test_get_token_no_provider(self):
        """Test that None is returned when not in any supported environment."""
        with patch.dict(os.environ, {}, clear=True), patch("boto3.client", side_effect=Exception("No boto3")):
            token = get_oidc_token()
            assert token is None

    def test_get_bitbucket_token(self):
        """Test getting a Bitbucket Pipelines OIDC token."""
        with patch.dict(
            os.environ,
            {
                "BITBUCKET_PIPELINE_UUID": "{12345678-1234-1234-1234-123456789012}",
                "BITBUCKET_STEP_OIDC_TOKEN": "bitbucket_token_abc",
            },
            clear=True,
        ):
            token = get_oidc_token()
            assert token == "bitbucket_token_abc"

    def test_get_jenkins_token(self):
        """Test getting a Jenkins OIDC token."""
        with patch.dict(
            os.environ,
            {
                "JENKINS_URL": "https://jenkins.example.com",
                "OIDC_TOKEN": "jenkins_token_xyz",
            },
            clear=True,
        ):
            token = get_oidc_token()
            assert token == "jenkins_token_xyz"


class TestExchangeOIDCToken:
    """Test suite for OIDC token exchange."""

    def test_exchange_token_success(self):
        """Test successful OIDC token exchange."""
        with patch("cloudsmith_cli.cli.oidc.requests.Session") as mock_session, \
             patch("getpass.getuser", return_value="testuser"), \
             patch("keyring.get_password", return_value=None), \
             patch("keyring.set_password"):
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
        with patch("cloudsmith_cli.cli.oidc.requests.Session") as mock_session, \
             patch("getpass.getuser", return_value="testuser"), \
             patch("keyring.get_password", return_value=None), \
             patch("keyring.set_password"):
            mock_response = MagicMock()
            mock_response.json.return_value = {"access_token": "cloudsmith_token_789"}
            mock_response.raise_for_status = MagicMock()
            mock_session.return_value.post.return_value = mock_response

            token = exchange_oidc_token(
                "https://api.cloudsmith.io", "oidc_token_456", "my-org"
            )
            assert token == "cloudsmith_token_789"
            mock_response.raise_for_status = MagicMock()
            mock_session.return_value.post.return_value = mock_response

            token = exchange_oidc_token(
                "https://api.cloudsmith.io", "oidc_token_456", "my-org"
            )
            assert token == "cloudsmith_token_789"
