"""Command functionality."""
# we're just going to use click

import importlib
import inspect
import pathlib
import sys

import click

import utils.network
import utils.values
import widgets.terminal


def get_commands() -> dict[str, click.Command]:
    """Get all commands."""
    results: dict[str, click.Command] = {}
    for file in pathlib.Path("commands").iterdir():
        filename: str = f"commands.{file.name.removesuffix('.py')}"
        debug: bool = filename == "commands.debug"
        if not debug or utils.values.GAME_VALUES.debug:
            importlib.import_module(filename)
            objects: list[tuple[str, click.Command]] = inspect.getmembers(
                sys.modules[filename], lambda object: isinstance(object, click.Command))
            for name, obj in objects:
                if not obj.name is None:
                    name = obj.name
                obj.add_help_option = False
                results[name] = obj
    return results


async def parse(text: str) -> None:
    """Parse cli input."""
    chunks: list[str] = text.strip().split()
    cmd_name: str = chunks[0]
    args: list[str] = chunks[1:]
    if COMMANDS.get(cmd_name) is not None:
        try:
            cmd_ret = COMMANDS[cmd_name](args, standalone_mode=False,
                                         help_option_names=[])
            if inspect.isawaitable(cmd_ret):
                await cmd_ret
        except Exception as excp:  # pylint:disable=broad-exception-caught
            print(f"Error: {excp}")
        finally:
            print(utils.network.NETWORK.computer.prompt)
    else:
        print(f"Error: {cmd_name} is not a known command.")
        print(utils.network.NETWORK.computer.prompt)


def clear() -> None:
    """Clear the terminal."""
    widgets.terminal.Terminal.TERMINAL.clear()


async def input(prompt: str) -> str:  # pylint:disable=redefined-builtin
    """Get an input from the terminal."""
    return await widgets.terminal.Terminal.TERMINAL.get_input(prompt)


def print(text: str) -> None:  # pylint:disable=redefined-builtin
    """Write to console."""
    widgets.terminal.Terminal.TERMINAL.write_lines(text)


COMMANDS = get_commands()
