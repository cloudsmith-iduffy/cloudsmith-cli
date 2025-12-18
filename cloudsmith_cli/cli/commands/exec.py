"""CLI/Commands - Execute package manager commands with automatic credential injection."""

import os
import subprocess
import sys

import click

from ...core import credentials as creds_module
from .. import decorators
from .main import main


# Package manager configurations
PACKAGE_MANAGERS = {
    "npm": {
        "name": "npm",
        "env_var": "NPM_TOKEN",
        "description": "Node Package Manager",
    },
    "mvn": {
        "name": "mvn",
        "env_var": "CLOUDSMITH_TOKEN",
        "description": "Apache Maven",
    },
    "maven": {
        "name": "mvn",
        "env_var": "CLOUDSMITH_TOKEN",
        "description": "Apache Maven",
    },
    "gradle": {
        "name": "gradle",
        "env_var": "CLOUDSMITH_TOKEN",
        "description": "Gradle",
    },
    "composer": {
        "name": "composer",
        "env_var": "COMPOSER_AUTH_TOKEN",
        "description": "PHP Composer",
    },
    "cargo": {
        "name": "cargo",
        "env_var": "CARGO_REGISTRIES_CLOUDSMITH_TOKEN",
        "description": "Rust Cargo",
    },
    "sbt": {
        "name": "sbt",
        "env_var": "CLOUDSMITH_TOKEN",
        "description": "Scala SBT",
    },
    "pip": {
        "name": "pip",
        "env_var": "PIP_INDEX_URL_TOKEN",
        "description": "Python pip",
    },
    "uv": {
        "name": "uv",
        "env_var": "UV_INDEX_URL_TOKEN",
        "description": "Python uv",
    },
    "poetry": {
        "name": "poetry",
        "env_var": "POETRY_HTTP_BASIC_CLOUDSMITH_PASSWORD",
        "description": "Python Poetry",
    },
    "nuget": {
        "name": "nuget",
        "env_var": "NUGET_CLOUDSMITH_TOKEN",
        "description": ".NET NuGet",
    },
    "dotnet": {
        "name": "dotnet",
        "env_var": "NUGET_CLOUDSMITH_TOKEN",
        "description": ".NET CLI",
    },
    "terraform": {
        "name": "terraform",
        "env_var": "TF_TOKEN_cloudsmith_io",
        "description": "Terraform",
    },
    "conan": {
        "name": "conan",
        "env_var": "CONAN_PASSWORD",
        "description": "Conan C/C++",
    },
    "docker": {
        "name": "docker",
        "env_var": "DOCKER_PASSWORD",
        "description": "Docker",
    },
    "helm": {
        "name": "helm",
        "env_var": "HELM_REGISTRY_PASSWORD",
        "description": "Helm",
    },
}


@main.command(name="exec")
@click.argument("package_manager", type=click.Choice(list(PACKAGE_MANAGERS.keys())))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "--oidc-slug",
    "oidc_slug",
    default=None,
    help="The service slug (organization) for OIDC token exchange.",
)
@decorators.common_cli_config_options
@decorators.common_cli_output_options
@decorators.initialise_api
@click.pass_context
def exec_command(ctx, opts, package_manager, args, oidc_slug):
    """
    Execute a package manager command with automatic credential injection.

    This command wraps package manager commands and automatically injects
    Cloudsmith credentials via environment variables. This eliminates the need
    for manual credential configuration.

    Examples:

        \b
        cloudsmith exec npm install
        cloudsmith exec mvn clean install
        cloudsmith exec composer update
        cloudsmith exec cargo build

    You can also create aliases for seamless integration:

        \b
        alias npm="cloudsmith exec npm"
        alias mvn="cloudsmith exec mvn"

    Supported package managers:
    npm, maven/mvn, gradle, composer, cargo, sbt, pip, uv, poetry,
    nuget, dotnet, terraform, conan, docker, helm
    """
    pm_config = PACKAGE_MANAGERS[package_manager]

    # Get credentials using the credential provider chain
    credentials = creds_module.get_credentials(opts=opts, oidc_slug=oidc_slug)

    if not credentials:
        click.secho(
            f"No credentials found. Please authenticate using 'cloudsmith login'",
            fg="red",
            err=True,
        )
        ctx.exit(1)

    # Prepare environment with injected credentials
    env = os.environ.copy()
    env[pm_config["env_var"]] = credentials.api_key

    # For some package managers, we may need additional env vars
    if package_manager in ("npm", "uv", "pip"):
        # npm/uv/pip might use different env var patterns
        env["CLOUDSMITH_API_KEY"] = credentials.api_key
    elif package_manager == "docker":
        # Docker might also need username
        env["DOCKER_USERNAME"] = "token"

    if opts.debug:
        click.echo(
            f"Debug: Executing {pm_config['name']} with credentials from {credentials.source}",
            err=True,
        )
        click.echo(f"Debug: Environment variable: {pm_config['env_var']}", err=True)

    # Execute the package manager command
    try:
        cmd = [pm_config["name"]] + list(args)
        result = subprocess.run(cmd, env=env, check=False)
        ctx.exit(result.returncode)
    except FileNotFoundError:
        click.secho(
            f"Error: {pm_config['name']} command not found. "
            f"Please ensure {pm_config['description']} is installed.",
            fg="red",
            err=True,
        )
        ctx.exit(127)
    except Exception as exc:  # pylint: disable=broad-except
        click.secho(
            f"Error executing {pm_config['name']}: {exc}",
            fg="red",
            err=True,
        )
        ctx.exit(1)
