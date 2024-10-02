"""Command functionality."""
# we're just going to use click

import importlib
import inspect
import pathlib
import sys

import click

import main
import widgets
import widgets.terminal


@click.command(add_help_option=False)
@click.argument("command", type=click.STRING, default="")
def help(command: str) -> str:  # pylint:disable=redefined-builtin
    """Show a list of all commands."""
    if command == "":
        return "\n".join([f"{name:10} {cmd.__doc__}"
                          for name, cmd in COMMANDS.items()])
    if command in COMMANDS:
        return str(COMMANDS[command].get_help(click.Context(COMMANDS[command])))
    return f"No help exists for '{command}'."


def get_commands() -> dict[str, click.Command]:
    """Get all commands."""
    results: dict[str, click.Command] = {"help": help}
    for file in pathlib.Path("commands").iterdir():
        filename: str = f"commands.{file.name.removesuffix('.py')}"
        importlib.import_module(filename)
        for name, obj in inspect.getmembers(sys.modules[filename]):
            if isinstance(obj, click.Command):
                obj.add_help_option = False
                results[name] = obj
    return results


COMMANDS: dict[str, click.Command] = get_commands()
ORACLE: main.OracleApp
TERMINAL: widgets.terminal.Terminal


def parse(text: str) -> str | None:
    """Parse cli input."""
    chunks: list[str] = text.strip().split()
    cmd_name: str = chunks[0]
    args: list[str] = chunks[1:]
    if COMMANDS.get(cmd_name) is not None:
        try:
            return COMMANDS[cmd_name](args, standalone_mode=False, help_option_names=[])
        except Exception as excp:  # pylint:disable=broad-exception-caught
            return f"Error: {excp}"
    return f"Error: {cmd_name} is not a known command."
