#!/bin/bash
# npm wrapper with Cloudsmith authentication

# Get token from cloudsmith CLI
TOKEN=$(cloudsmith tokens get ${CLOUDSMITH_OIDC_SLUG:+--oidc-slug $CLOUDSMITH_OIDC_SLUG})

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to get Cloudsmith token" >&2
    exit 1
fi

# Configure npm authentication
npm config set //npm.cloudsmith.io/:_authToken "$TOKEN"

# Run npm command
npm "$@"
