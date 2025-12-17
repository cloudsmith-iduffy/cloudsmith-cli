#!/bin/bash
# Dart pub wrapper with Cloudsmith authentication

# Get token from cloudsmith CLI
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to get Cloudsmith token" >&2
    exit 1
fi

# Set environment variable for dart pub
export CLOUDSMITH_TOKEN="$TOKEN"

# Ensure token is configured (idempotent)
if [ -n "$CLOUDSMITH_REPO_URL" ]; then
    dart pub token add "$CLOUDSMITH_REPO_URL" --env-var CLOUDSMITH_TOKEN 2>/dev/null || true
fi

# Run dart pub command
dart pub "$@"
