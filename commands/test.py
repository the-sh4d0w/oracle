"""Command test stuff."""

import click


@click.command()
@click.argument("text")
@click.option("-u", "--upper", is_flag=True)
def echo(text: str, upper: bool) -> str:
    """Just echoes input."""
    if upper:
        return text.upper()
    return text
