#!/usr/bin/env elixir
# Cloudsmith Hex Credential Helper
#
# This script retrieves a Cloudsmith token for use with Hex.
#
# Usage:
#   export HEX_API_KEY=$(./cloudsmith-hex-creds.exs)

defmodule CloudsmithHex do
  def get_token do
    oidc_slug = System.get_env("CLOUDSMITH_OIDC_SLUG")
    
    cmd_args = if oidc_slug do
      ["cloudsmith", "tokens", "get", "--oidc-slug", oidc_slug]
    else
      ["cloudsmith", "tokens", "get"]
    end
    
    case System.cmd(List.first(cmd_args), Enum.drop(cmd_args, 1), stderr_to_stdout: true) do
      {token, 0} ->
        String.trim(token)
      {error, _} ->
        IO.puts(:stderr, "Error getting token: #{error}")
        System.halt(1)
    end
  rescue
    e in ErlangError ->
      IO.puts(:stderr, "cloudsmith CLI not found. Install: pip install cloudsmith-cli")
      System.halt(1)
  end
end

IO.puts(CloudsmithHex.get_token())
