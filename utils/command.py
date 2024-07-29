"""Command functionality."""
# we're just going to use click

import importlib
import inspect
import pathlib
import sys
import typing


def get_commands() -> dict[str, typing.Callable]:
    """Get all commands."""
    # maybe replace with a more sophisticated method
    results: dict[str, typing.Callable] = {}
    for file in pathlib.Path("commands").iterdir():
        filename: str = f"commands.{file.name.removesuffix('.py')}"
        importlib.import_module(filename)
        for name, obj in inspect.getmembers(sys.modules[filename]):
            if isinstance(obj, typing.Callable):
                results[name] = obj
    return results


COMMANDS: dict[str, typing.Callable] = get_commands()


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
