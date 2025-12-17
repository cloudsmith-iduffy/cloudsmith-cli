#!/bin/bash
"""
Conda Authentication Helper for Cloudsmith

This script generates .netrc entries for Cloudsmith Conda repositories.

Usage:
    ./setup-conda-auth.sh

Environment Variables:
    CLOUDSMITH_OIDC_SLUG: Organization slug for OIDC authentication (optional)
"""

# Get token from Cloudsmith CLI
if [ -n "$CLOUDSMITH_OIDC_SLUG" ]; then
    TOKEN=$(cloudsmith tokens get --oidc-slug "$CLOUDSMITH_OIDC_SLUG")
else
    TOKEN=$(cloudsmith tokens get)
fi

if [ -z "$TOKEN" ]; then
    echo "Error: Could not retrieve Cloudsmith token"
    exit 1
fi

# Backup existing .netrc
if [ -f ~/.netrc ]; then
    cp ~/.netrc ~/.netrc.backup
    echo "Backed up existing .netrc to ~/.netrc.backup"
fi

# Add Cloudsmith entry to .netrc
cat >> ~/.netrc << EOF
machine conda.cloudsmith.io
  login token
  password $TOKEN
EOF

chmod 600 ~/.netrc

echo "Successfully configured Conda authentication for Cloudsmith"
echo "Token will be used for conda.cloudsmith.io"
