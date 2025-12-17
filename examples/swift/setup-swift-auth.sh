#!/bin/bash
# Setup Swift Package Manager authentication for Cloudsmith

# Get token from cloudsmith CLI
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to get Cloudsmith token" >&2
    exit 1
fi

# Create or update .netrc file
NETRC_FILE="$HOME/.netrc"
NETRC_ENTRY="machine swift.cloudsmith.io
login token
password $TOKEN"

# Remove existing Cloudsmith entry if present
if [ -f "$NETRC_FILE" ]; then
    # Create temp file without Cloudsmith entries
    if grep -v "swift.cloudsmith.io" "$NETRC_FILE" > "$NETRC_FILE.tmp" 2>/dev/null; then
        mv "$NETRC_FILE.tmp" "$NETRC_FILE"
    else
        # If grep found nothing or failed, create empty file
        touch "$NETRC_FILE"
    fi
fi

# Add new entry
echo "$NETRC_ENTRY" >> "$NETRC_FILE"

# Set proper permissions
chmod 600 "$NETRC_FILE"

echo "Swift authentication configured successfully"
echo "Token will expire in ~12 hours - re-run this script to refresh"
