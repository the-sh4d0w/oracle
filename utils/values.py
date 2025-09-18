"""Value stuff."""

import dataclasses

import utils.network


@dataclasses.dataclass
class GameValues:
    """Game values."""

    def __init__(self) -> None:
        """Initialise game values."""
        self.debug: bool = False
        self.noboot: bool = False


@dataclasses.dataclass
class TextValues:
    """Values for text formatting."""
    player: str | None = None  # generally available; assign in login
    user: str | None = None  # current user on computer; set when changed in computer
    name: str | None = None  # current computer name; set when changed in computer
    path: str | None = None  # current path on computer; set when changed in computer

    def update(self) -> None:
        """Update values."""
        self.user = utils.network.NETWORK.computer.username
        self.name = utils.network.NETWORK.computer.name
        self.path = utils.network.NETWORK.computer.file_system.pwd()

    def as_dict(self) -> dict[str, str | None]:
        """Get values as dict. Also updates values."""
        self.update()
        return self.__dict__


GAME_VALUES = GameValues()
VALUES = TextValues()
