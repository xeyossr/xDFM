import os
import click
import sys
import colorama
from pathlib import Path
from modules import dfm
colorama.init()

global home_dir, dot_config_dir, config_dir, config_file

home_dir = dfm.home_dir
main = home_dir
dot_config_dir = dfm.dot_config_dir
config_dir = dfm.config_dir
config_file = Path(os.path.join(config_dir, 'xdfm.conf'))

class OrderedGroup(click.Group):
    def list_commands(self, ctx):
        return list(self.commands)

# Main command
@click.group(cls=OrderedGroup)
@click.version_option(version=dfm.__version__)
def xdfm():
    """xdfm - Xeyossr Dotfiles Manager."""
    pass


# GitHub sub-command group
@click.group()
def github():
    """Commands related to GitHub operations"""
    pass


@github.command()
@click.argument('repo_name')
@click.option('--commit', default="Initial commit", help="Commit message")
@click.option('--path', default=main, help="Dotfiles directory path")
def create(repo_name, commit, path):
    """Create GitHub `dotfiles` repository."""
    dfm.create_repo(repo_name, config_file, path, commit)


@github.command()
@click.argument('pat_token')
def pat(pat_token):
    """Define personal access token for GitHub"""
    click.echo(f"{colorama.Fore.YELLOW}Setting GitHub PAT to {pat_token}")
    dfm.edit_config(config_file, 'GitHub', 'pat', pat_token)
    dfm.edit_config(config_file, 'Settings', 'PAT_Alert', 'disabled')

# Add folder command
@xdfm.command()
@click.argument('value')
@click.argument('key', required=False, default=None)
def add(value, key):
    """Add a new dot folder path to the config file."""
    click.echo(f"{colorama.Fore.YELLOW}Adding folder: `{colorama.Fore.GREEN}{value}{colorama.Fore.YELLOW}`")
    dfm.add_config(config_file, 'Dots', value, key)


# Remove folder command
@xdfm.command()
@click.argument('key')
def remove(key):
    """Remove an existing dot folder path from the config file."""
    click.echo(f"{colorama.Fore.YELLOW}Removing `{colorama.Fore.GREEN}{key}{colorama.Fore.YELLOW}`")
    dfm.remove_config(config_file, 'Dots', key)

# List command
@xdfm.command(name="list")
def list_command():
    """List all dot folder paths present in the config file"""
    dfm.list(config_file)

# Edit command
@xdfm.command()
@click.argument('key')
@click.argument('value')
def edit(key, value):
    """Edit the path of an existing dot folder in the config."""
    click.echo(f"{colorama.Fore.YELLOW}Editing `{colorama.Fore.GREEN}{key}{colorama.Fore.YELLOW}` to `{colorama.Fore.GREEN}{value}{colorama.Fore.YELLOW}`")
    dfm.edit_config(config_file, 'Dots', key, value)


@xdfm.command()
@click.argument('editor', required=False, default='nano')
def editconfig(editor):
    """Edit the config file with the specified editor (default: nano)"""
    dfm.edit_configfile(config_file, editor)

# Create dotfiles directory
@xdfm.command()
@click.option('--path', default=main, help='Dotfiles folder path')
@click.option('--name', default='dotfiles')
def create(path, name):
    """Create the dotfiles directory"""
    click.echo(f"{colorama.Fore.GREEN}Creating dotfiles...")
    dfm.create_dotfiles(config_file, path, name)

@xdfm.command()
@click.argument('path')
def update(path):
    """Update the dotfiles directory"""
    dfm.update_dotfiles(config_file, path)


@xdfm.command()
def info():
    """Some important information."""
    click.echo("Some information")
    click.echo("\n- When adding a file with 'add', if the key is not equal to the name of the file and there is no space or extension in the key, it will create a folder with that name and put the file there.")
    click.echo("\n- When adding a folder/file with the 'add' command, if you set the key to something like '.config/waybar', it will create a folder named .config and copy that file/folder into it.")


# Add the github commands to the main xdfm command
xdfm.add_command(github)

if __name__ == '__main__':
    xdfm()