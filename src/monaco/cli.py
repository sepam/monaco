import click

# from monaco import __version__



# @click.version_option(version=__version__)
@click.command()
@click.version_option(version="0.1.1")
def main():
    """The Monaco project."""
    click.secho("Welcome to Monaco -- an easier way to plan projects", fg='green')


if __name__ == '__main__':
    main()
