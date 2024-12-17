"""Save stuff."""

import datetime
import pathlib

import pydantic

SAVES_PATH = pathlib.Path("saves")


class Save(pydantic.BaseModel):
    """Save file representation."""
    username: str
    password: str
    money: int
    programs: list[str]
    files: list[str]

    @pydantic.computed_field
    @property
    def filename(self) -> str:
        """Filename of the save."""
        return f"{self.username}_{datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.json"

    def save(self) -> None:
        """Save the save as a file."""
        pathlib.Path.joinpath(SAVES_PATH, self.filename).write_text(
            data=self.model_dump_json(), encoding="utf-8")

    @classmethod
    def create(cls, username: str, password: str) -> "Save":
        """Create a new save.

        Arguments:
            - username: the username for the save.
            - password: the password for the save.

        Returns:
            The created save.
        """
        return Save(username=username, password=password, money=100, programs=[], files=[])


def get_newest_saves() -> dict[str, Save]:
    """Get the newest save for each user.

    Returns:
        The newest save for each user.
    """
    result: dict[str, Save] = {}
    # should work; sorted alphabetically then reversed
    for file in reversed(list(SAVES_PATH.iterdir())):
        save = Save.model_validate_json(file.read_text(encoding="utf-8"))
        user: str = file.name.split("_")[0]
        if result.get(user) is None:
            result[user] = save
    return result
