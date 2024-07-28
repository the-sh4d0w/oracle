"""Command stuff."""

import typing

import main

import widgets.terminal


class Command:
    """Command for the terminal."""

    COMMANDS: list["Command"] = []
    terminal: widgets.terminal.Terminal
    oracle: main.OracleApp

    def __init__(self, name: str, help_text: str) -> None:
        """Initialize the command."""
        self.name: str = name
        self.help_text: str = help_text

    def run(self) -> str | None:
        """Run method, has to be replaced.

        Arguments:
            - ??? -> what did I want to do here?
        """
        raise NotImplementedError()

    @classmethod
    def create_simple_command(cls) -> typing.Callable:
        """Create a simple command."""
        def __command(func: typing.Callable[[], str | None]) -> "Command":
            command = Command(func.__name__.removesuffix("_"),
                              "" if func.__doc__ is None else func.__doc__)
            command.run = func
            cls.COMMANDS.append(command)
            return command
        return __command
