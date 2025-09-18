"""Shared values."""


import click

import utils.command
import utils.network
import widgets.terminal


class SharedValues:
    """Shared values."""

    def __init__(self) -> None:
        """Initialise the shared values."""
        self._commands: dict[str, click.Command] = utils.command.get_commands()
        self._network: utils.network.Network = utils.network.Network()
        self._terminal: widgets.terminal.Terminal

    def _notify(self) -> None:
        """Notify all observers."""

    @property
    def commands(self) -> dict[str, click.Command]:
        """All commands."""
        return self._commands

    @property
    def network(self) -> utils.network.Network:
        """The network."""
        return self._network

    @property
    def terminal(self) -> widgets.terminal.Terminal:
        """The terminal widget."""
        return self._terminal

    @terminal.setter
    def terminal(self, value: widgets.terminal.Terminal) -> None:
        """Set the terminal."""
        self._terminal = value


SHARED = SharedValues()
