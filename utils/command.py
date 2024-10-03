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

ORACLE: main.OracleApp
TERMINAL: widgets.terminal.Terminal


def get_commands(debug: bool) -> dict[str, click.Command]:
    """Get all commands."""
    results: dict[str, click.Command] = dict()
    for file in pathlib.Path("commands").iterdir():
        filename: str = f"commands.{file.name.removesuffix('.py')}"
        if filename != "commands.debug" or debug:
            importlib.import_module(filename)
            for name, obj in inspect.getmembers(sys.modules[filename]):
                if isinstance(obj, click.Command):
                    obj.add_help_option = False
                    results[name] = obj
    return results


def parse(oracle: main.OracleApp, text: str) -> str | None:
    """Parse cli input."""
    chunks: list[str] = text.strip().split()
    cmd_name: str = chunks[0]
    args: list[str] = chunks[1:]
    if oracle.commands.get(cmd_name) is not None:
        try:
            return oracle.commands[cmd_name](args, standalone_mode=False, help_option_names=[])
        except Exception as excp:  # pylint:disable=broad-exception-caught
            return f"Error: {excp}"
    return f"Error: {cmd_name} is not a known command."
