import os
from unittest.mock import patch

import cloudsmith_api
import pytest

from cloudsmith_cli.cli.commands.tokens import get, list_tokens, refresh
from cloudsmith_cli.core.api.exceptions import ApiException


class MockToken:
    """Mock Token object with the properties needed for testing."""

    def __init__(self, key, created, slug_perm):
        self.key = key
        self.created = created
        self.slug_perm = slug_perm


@pytest.mark.usefixtures("set_api_host_env_var")
class TestListTokensCommand:

    def test_list_tokens_success(self, runner):
        """Test successful listing of tokens."""
        mock_tokens = [
            MockToken(
                key="abc123", created="2025-01-01T00:00:00Z", slug_perm="token-1"
            ),
            MockToken(
                key="def456", created="2025-01-02T00:00:00Z", slug_perm="token-2"
            ),
        ]

        with patch("cloudsmith_cli.core.api.user.list_user_tokens") as mock_list_tokens:
            mock_list_tokens.return_value = mock_tokens
            result = runner.invoke(list_tokens, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Retrieving API tokens... OK" in result.output
        assert "Token: abc123" in result.output
        assert "Created: 2025-01-01T00:00:00Z" in result.output
        assert "slug_perm: token-1" in result.output
        assert "Token: def456" in result.output
        assert "Created: 2025-01-02T00:00:00Z" in result.output
        assert "slug_perm: token-2" in result.output

    def test_list_tokens_error(self, runner):
        """Test error handling when listing tokens fails."""
        with patch("cloudsmith_cli.core.api.user.list_user_tokens") as mock_list_tokens:
            # Use ApiException for proper error handling
            mock_list_tokens.side_effect = ApiException("API error")
            result = runner.invoke(list_tokens, [], catch_exceptions=True)

        assert result.exit_code != 0

        # The error message might be in different places depending on how the exception is raised
        # Note: stderr is mixed into output with default CliRunner
        error_content = str(getattr(result, "exception", "")) + result.output
        assert (
            "API error" in error_content
            or "Failed to retrieve API tokens" in error_content
        )


@pytest.mark.usefixtures("set_api_host_env_var")
class TestRefreshTokenCommand:
    """Test suite for the 'tokens refresh' command."""

    def test_refresh_token_with_slug(self, runner):
        """Test successful refreshing of a token with a provided slug."""
        mock_new_token = MockToken(
            key="new_token_123",
            created="2025-01-03T00:00:00Z",
            slug_perm="token-refresh",
        )

        with patch(
            "cloudsmith_cli.core.api.user.refresh_user_token"
        ) as mock_refresh_token:
            mock_refresh_token.return_value = mock_new_token
            result = runner.invoke(refresh, ["token-refresh"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Refreshing token token-refresh... OK" in result.output
        assert "New token value: new_token_123" in result.output
        mock_refresh_token.assert_called_once_with("token-refresh")

    def test_refresh_token_error(self, runner):
        """Test error handling when refreshing a token fails."""
        with patch(
            "cloudsmith_cli.core.api.user.refresh_user_token"
        ) as mock_refresh_token:
            # Use ApiException for proper error handling
            mock_refresh_token.side_effect = ApiException("API error")
            result = runner.invoke(refresh, ["token-error"], catch_exceptions=True)

        assert result.exit_code != 0

        # The error message might be in different places depending on how the exception is raised
        # Note: stderr is mixed into output with default CliRunner
        error_content = str(getattr(result, "exception", "")) + result.output
        assert (
            "API error" in error_content
            or "Failed to refresh the token" in error_content
        )

    def test_refresh_token_list_error(self, runner):
        """Test error handling when listing tokens fails during refresh."""
        with patch("cloudsmith_cli.core.api.user.list_user_tokens") as mock_list_tokens:
            # Use ApiException for proper error handling
            mock_list_tokens.side_effect = ApiException("API error")
            result = runner.invoke(refresh, [], catch_exceptions=True)

        assert result.exit_code != 0

        # The error message might be in different places depending on how the exception is raised
        # Note: stderr is mixed into output with default CliRunner
        error_content = str(getattr(result, "exception", "")) + result.output
        assert (
            "API error" in error_content
            or "Failed to refresh the token" in error_content
        )


class TestGetTokenCommand:
    """Test suite for the 'tokens get' command."""

    @pytest.fixture(autouse=True)
    def cleanup_api_config(self):
        """Clean up API configuration before and after each test to avoid pollution."""
        # Reset before the test
        try:
            config = cloudsmith_api.Configuration()
            if hasattr(config, "api_key"):
                config.api_key = {}
            cloudsmith_api.Configuration.set_default(config)
        except (AttributeError, KeyError):
            # Ignore errors during cleanup
            pass

        yield

        # Reset after the test
        try:
            config = cloudsmith_api.Configuration()
            if hasattr(config, "api_key"):
                config.api_key = {}
            cloudsmith_api.Configuration.set_default(config)
        except (AttributeError, KeyError):
            # Ignore errors during cleanup
            pass

    def test_get_token_with_api_key(self, runner):
        """Test getting token when API key is set."""
        with patch.dict(
            os.environ, {"CLOUDSMITH_API_HOST": "https://api.cloudsmith.io"}
        ):
            result = runner.invoke(
                get, ["-k", "test_api_key_123"], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert result.output.strip() == "test_api_key_123"

    def test_get_token_with_saml(self, runner):
        """Test getting token when SAML access token exists in keyring."""
        # Temporarily remove any API key from environment
        saved_api_key = os.environ.pop("CLOUDSMITH_API_KEY", None)
        try:
            with patch(
                "cloudsmith_cli.core.keyring.get_access_token"
            ) as mock_get_access_token, patch(
                "cloudsmith_cli.core.keyring.should_refresh_access_token"
            ) as mock_should_refresh, patch.dict(
                os.environ, {"CLOUDSMITH_API_HOST": "https://api.cloudsmith.io"}
            ):
                mock_get_access_token.return_value = "saml_access_token_456"
                mock_should_refresh.return_value = False

                result = runner.invoke(get, [], catch_exceptions=False)

            assert result.exit_code == 0
            assert result.output.strip() == "saml_access_token_456"
        finally:
            if saved_api_key:
                os.environ["CLOUDSMITH_API_KEY"] = saved_api_key

    def test_get_token_no_auth(self, runner):
        """Test getting token when no authentication is available."""
        saved_api_key = os.environ.pop("CLOUDSMITH_API_KEY", None)
        try:
            with patch(
                "cloudsmith_cli.core.keyring.get_access_token"
            ) as mock_get_access_token, patch(
                "cloudsmith_cli.cli.commands.tokens.detect_oidc_provider"
            ) as mock_detect_oidc, patch.dict(
                os.environ, {"CLOUDSMITH_API_HOST": "https://api.cloudsmith.io"}
            ):
                mock_get_access_token.return_value = None
                mock_detect_oidc.return_value = (None, None)

                result = runner.invoke(get, [], catch_exceptions=False)

            assert result.exit_code == 1
            assert "No authentication token found" in result.output
        finally:
            if saved_api_key:
                os.environ["CLOUDSMITH_API_KEY"] = saved_api_key

    def test_get_token_with_oidc(self, runner):
        """Test getting token with OIDC in any environment."""
        saved_api_key = os.environ.pop("CLOUDSMITH_API_KEY", None)
        try:
            with patch(
                "cloudsmith_cli.core.keyring.get_access_token"
            ) as mock_get_access_token, patch(
                "cloudsmith_cli.cli.commands.tokens.detect_oidc_provider"
            ) as mock_detect_oidc, patch(
                "cloudsmith_cli.cli.commands.tokens.get_oidc_token"
            ) as mock_get_oidc, patch(
                "cloudsmith_cli.cli.commands.tokens.exchange_oidc_token"
            ) as mock_exchange, patch.dict(
                os.environ, {"CLOUDSMITH_API_HOST": "https://api.cloudsmith.io"}
            ):

                mock_get_access_token.return_value = None
                mock_detect_oidc.return_value = (
                    "github",
                    "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
                )
                mock_get_oidc.return_value = "github_oidc_token"
                mock_exchange.return_value = "cloudsmith_token_789"

                result = runner.invoke(
                    get, ["--oidc-slug", "my-org"], catch_exceptions=False
                )

            assert result.exit_code == 0
            assert result.output.strip() == "cloudsmith_token_789"
        finally:
            if saved_api_key:
                os.environ["CLOUDSMITH_API_KEY"] = saved_api_key
