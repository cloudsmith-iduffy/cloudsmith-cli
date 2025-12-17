#!/bin/bash
# Setup Go modules authentication for Cloudsmith

# Get token from cloudsmith CLI
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to get Cloudsmith token" >&2
    exit 1
fi

# Create or update .netrc file
NETRC_FILE="$HOME/.netrc"
NETRC_ENTRY="machine go.cloudsmith.io
login token
password $TOKEN"

# Remove existing Cloudsmith entry if present
if [ -f "$NETRC_FILE" ]; then
    # Create temp file without Cloudsmith entries
    grep -v "go.cloudsmith.io" "$NETRC_FILE" > "$NETRC_FILE.tmp" || true
    mv "$NETRC_FILE.tmp" "$NETRC_FILE"
fi

# Add new entry
echo "$NETRC_ENTRY" >> "$NETRC_FILE"

# Set proper permissions
chmod 600 "$NETRC_FILE"

echo "Go modules authentication configured successfully"
echo "Token will expire in ~12 hours - re-run this script to refresh"
echo ""
echo "Don't forget to set:"
echo "  export GOPRIVATE=\"go.cloudsmith.io/my-org/*\""
