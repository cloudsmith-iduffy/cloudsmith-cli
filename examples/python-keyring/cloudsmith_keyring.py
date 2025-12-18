"""
Cloudsmith Keyring Backend for Python/pip/uv

A keyring backend that provides automatic authentication for Cloudsmith Python
repositories using the `cloudsmith tokens get` command.

This is similar to Microsoft's artifacts-keyring but for Cloudsmith.

Installation:
    pip install cloudsmith-cli
    pip install keyring
    
    # Install this backend
    pip install -e .
    
    # Or copy cloudsmith_keyring.py to your Python site-packages

Usage:
    Once installed, pip and other tools that use keyring will automatically
    use this backend for Cloudsmith repositories.
    
    # Install from Cloudsmith
    pip install --index-url https://python.cloudsmith.io/my-org/my-repo/simple/ my-package
    
    # No manual authentication required!

Environment Variables:
    CLOUDSMITH_OIDC_SLUG: Organization slug for OIDC authentication (optional)
    CLOUDSMITH_API_KEY: API key for authentication (optional)

Reference:
    https://github.com/microsoft/artifacts-keyring
    https://pypi.org/project/keyring/
"""

import os
import subprocess
from typing import Optional

try:
    from keyring.backend import KeyringBackend
    from keyring.credentials import SimpleCredential
    from keyring.errors import PasswordDeleteError
except ImportError:
    raise ImportError(
        "keyring package is required. Install with: pip install keyring"
    )


class CloudsmithKeyringBackend(KeyringBackend):
    """
    Keyring backend for Cloudsmith Python repositories.
    
    This backend provides authentication for Cloudsmith by calling
    `cloudsmith tokens get` to retrieve the current authentication token.
    """
    
    # Priority for this backend (higher = more preferred)
    # Set to a high value so it's used for Cloudsmith URLs
    priority = 10
    
    def __init__(self):
        super().__init__()
        self._oidc_slug = os.environ.get("CLOUDSMITH_OIDC_SLUG")
    
    @classmethod
    def is_cloudsmith_url(cls, service):
        """Check if the service URL is a Cloudsmith repository."""
        if not service:
            return False
        return "cloudsmith.io" in service.lower()
    
    def get_password(self, service, username):
        """
        Get password (token) for the given service and username.
        
        Args:
            service: The service name (usually a URL)
            username: The username (ignored for Cloudsmith)
            
        Returns:
            str: The authentication token, or None if not a Cloudsmith service
        """
        # Only handle Cloudsmith services
        if not self.is_cloudsmith_url(service):
            return None
        
        try:
            return self._get_cloudsmith_token()
        except Exception:
            # If token retrieval fails, return None to allow fallback
            return None
    
    def get_credential(self, service, username):
        """
        Get credential (username and password) for the given service.
        
        Args:
            service: The service name (usually a URL)
            username: The username (optional)
            
        Returns:
            SimpleCredential: Credential with username and password, or None
        """
        # Only handle Cloudsmith services
        if not self.is_cloudsmith_url(service):
            return None
        
        try:
            token = self._get_cloudsmith_token()
            if token:
                # For Cloudsmith, username doesn't matter (usually "token" or anything)
                # pip will use whatever username is provided or default to "token"
                return SimpleCredential(username or "token", token)
        except Exception:
            pass
        
        return None
    
    def set_password(self, service, username, password):
        """
        Set password (not implemented - tokens are fetched on-demand).
        
        Args:
            service: The service name
            username: The username
            password: The password
        """
        # We don't store passwords, they're fetched on-demand
        # This is called by pip when using --index-url with credentials
        # We can safely ignore it
        pass
    
    def delete_password(self, service, username):
        """
        Delete password (not implemented - tokens are fetched on-demand).
        
        Args:
            service: The service name
            username: The username
            
        Raises:
            PasswordDeleteError: Always, as we don't store passwords
        """
        # We don't store passwords, so there's nothing to delete
        raise PasswordDeleteError("Cloudsmith keyring does not store passwords")
    
    def _get_cloudsmith_token(self) -> Optional[str]:
        """
        Get authentication token from Cloudsmith CLI.
        
        Returns:
            str: The authentication token
            
        Raises:
            Exception: If token retrieval fails
        """
        # Build the command
        cmd = ["cloudsmith", "tokens", "get"]
        
        # Add OIDC slug if provided
        if self._oidc_slug:
            cmd.extend(["--oidc-slug", self._oidc_slug])
        
        try:
            # Execute the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30  # 30 second timeout
            )
            token = result.stdout.strip()
            
            if not token:
                raise Exception("Empty token received from cloudsmith tokens get")
            
            return token
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get token: {e.stderr}")
        except FileNotFoundError:
            raise Exception(
                "cloudsmith CLI not found. Please install: pip install cloudsmith-cli"
            )
        except subprocess.TimeoutExpired:
            raise Exception("Token retrieval timed out")


# Register the backend
try:
    from keyring import set_keyring
    # Optionally set as default keyring (uncomment if desired)
    # set_keyring(CloudsmithKeyringBackend())
except ImportError:
    pass
