#!/usr/bin/env ruby
# Cloudsmith Bundler Credential Helper
# 
# This script provides credentials for Cloudsmith gem repositories.
#
# Usage:
#   export BUNDLE_GEMS__CLOUDSMITH__IO="token:$(ruby cloudsmith-bundler-creds.rb)"

require 'open3'

def get_cloudsmith_token
  cmd = ['cloudsmith', 'tokens', 'get']
  
  oidc_slug = ENV['CLOUDSMITH_OIDC_SLUG']
  cmd.concat(['--oidc-slug', oidc_slug]) if oidc_slug
  
  stdout, stderr, status = Open3.capture3(*cmd)
  
  if status.success?
    stdout.strip
  else
    warn "Error getting token: #{stderr}"
    exit 1
  end
rescue Errno::ENOENT
  warn "cloudsmith CLI not found. Install: pip install cloudsmith-cli"
  exit 1
end

if __FILE__ == $0
  puts get_cloudsmith_token
end
