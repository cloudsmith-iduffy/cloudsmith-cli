"""Credential Provider Chain for Cloudsmith CLI.

This module implements a pluggable credential provider chain similar to AWS CLI,
allowing credentials to be sourced from multiple locations in a prioritized order.
"""

import os
from typing import Optional, Dict, Any

from . import keyring
from ..cli.oidc import detect_oidc_provider, get_oidc_token, exchange_oidc_token
from ..cli.saml import create_configured_session


class Credentials:
    """Represents a set of credentials for Cloudsmith API authentication."""

    def __init__(
        self,
        api_key: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize credentials.

        Args:
            api_key: The API key/token for authentication
            source: The source of the credentials (e.g., "environment", "config", "saml")
            metadata: Additional metadata about the credentials
        """
        self.api_key = api_key
        self.source = source
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<Credentials source={self.source}>"


class CredentialProvider:
    """Base class for credential providers."""

    def __init__(self, name: str):
        """Initialize the provider with a name."""
        self.name = name

    def get_credentials(self, opts=None, **kwargs) -> Optional[Credentials]:
        """
        Retrieve credentials from this provider.

        Args:
            opts: CLI options object
            **kwargs: Additional provider-specific arguments

        Returns:
            Credentials object if successful, None otherwise
        """
        raise NotImplementedError


class EnvironmentCredentialProvider(CredentialProvider):
    """Provider that sources credentials from environment variables."""

    def __init__(self):
        super().__init__("environment")

    def get_credentials(self, opts=None, **kwargs) -> Optional[Credentials]:
        """Get credentials from CLOUDSMITH_API_KEY environment variable."""
        api_key = os.environ.get("CLOUDSMITH_API_KEY")
        if api_key:
            return Credentials(
                api_key=api_key,
                source="environment",
                metadata={"env_var": "CLOUDSMITH_API_KEY"},
            )
        return None


class ConfigFileCredentialProvider(CredentialProvider):
    """Provider that sources credentials from configuration files."""

    def __init__(self):
        super().__init__("config_file")

    def get_credentials(self, opts=None, **kwargs) -> Optional[Credentials]:
        """Get credentials from CLI options (which includes config file values)."""
        if opts and hasattr(opts, "api_key") and opts.api_key:
            return Credentials(
                api_key=opts.api_key,
                source="config_file",
                metadata={"config_path": getattr(opts, "config_path", None)},
            )
        return None


class SAMLCredentialProvider(CredentialProvider):
    """Provider that sources credentials from SAML authentication stored in keyring."""

    def __init__(self):
        super().__init__("saml")

    def get_credentials(self, opts=None, **kwargs) -> Optional[Credentials]:
        """Get credentials from keyring (SAML access token)."""
        if not opts:
            return None

        api_host = getattr(opts, "api_host", "https://api.cloudsmith.io")
        access_token = keyring.get_access_token(api_host)

        if access_token:
            return Credentials(
                api_key=access_token,
                source="saml",
                metadata={
                    "api_host": api_host,
                    "storage": "keyring",
                },
            )
        return None


class OIDCCredentialProvider(CredentialProvider):
    """Provider that sources credentials from OIDC token exchange."""

    def __init__(self):
        super().__init__("oidc")

    def get_credentials(self, opts=None, **kwargs) -> Optional[Credentials]:
        """
        Get credentials via OIDC token exchange.

        Requires oidc_slug to be provided in kwargs.
        """
        oidc_slug = kwargs.get("oidc_slug")
        if not oidc_slug:
            # OIDC requires organization slug, can't proceed without it
            return None

        provider = detect_oidc_provider()
        if not provider:
            return None

        oidc_token = get_oidc_token()
        if not oidc_token:
            return None

        try:
            api_host = getattr(opts, "api_host", "https://api.cloudsmith.io") if opts else "https://api.cloudsmith.io"
            session = create_configured_session(opts) if opts else None

            cloudsmith_token = exchange_oidc_token(
                api_host, oidc_token, oidc_slug, session=session
            )

            if cloudsmith_token:
                return Credentials(
                    api_key=cloudsmith_token,
                    source="oidc",
                    metadata={
                        "provider": provider,
                        "oidc_slug": oidc_slug,
                    },
                )
        except Exception:  # pylint: disable=broad-except
            # If OIDC exchange fails, fall through to next provider
            pass

        return None


class CredentialProviderChain:
    """
    Credential provider chain that tries multiple providers in order.

    Similar to AWS SDK credential provider chain, this tries providers
    in order until one succeeds or all fail.
    """

    def __init__(self, providers=None):
        """
        Initialize the credential provider chain.

        Args:
            providers: List of CredentialProvider instances. If None, uses default chain.
        """
        if providers is None:
            providers = [
                EnvironmentCredentialProvider(),
                ConfigFileCredentialProvider(),
                SAMLCredentialProvider(),
                OIDCCredentialProvider(),
            ]
        self.providers = providers

    def get_credentials(self, opts=None, **kwargs) -> Optional[Credentials]:
        """
        Try each provider in order until one returns credentials.

        Args:
            opts: CLI options object
            **kwargs: Additional arguments passed to providers

        Returns:
            Credentials object from first successful provider, or None if all fail
        """
        for provider in self.providers:
            try:
                credentials = provider.get_credentials(opts=opts, **kwargs)
                if credentials:
                    return credentials
            except Exception:  # pylint: disable=broad-except
                # If a provider fails, continue to next one
                continue

        return None

    def add_provider(self, provider: CredentialProvider, position: Optional[int] = None):
        """
        Add a provider to the chain.

        Args:
            provider: The CredentialProvider to add
            position: Position to insert at (None = append to end)
        """
        if position is None:
            self.providers.append(provider)
        else:
            self.providers.insert(position, provider)

    def remove_provider(self, provider_name: str):
        """Remove a provider from the chain by name."""
        self.providers = [p for p in self.providers if p.name != provider_name]


# Global default credential provider chain
_default_chain = CredentialProviderChain()


def get_credentials(opts=None, **kwargs) -> Optional[Credentials]:
    """
    Get credentials using the default credential provider chain.

    This is a convenience function that uses the global default chain.

    Args:
        opts: CLI options object
        **kwargs: Additional arguments (e.g., oidc_slug)

    Returns:
        Credentials object or None
    """
    return _default_chain.get_credentials(opts=opts, **kwargs)


def get_default_chain() -> CredentialProviderChain:
    """Get the default credential provider chain."""
    return _default_chain
