"""Scripting stuff."""

import pathlib

# TODO: implement

class Script:
    """Script."""

    def __init__(self, filepath: pathlib.Path | str) -> None:
        """Initialize the script.

        Arguments:
            - filepath: the path to the script file.
        """
        self.filepath = filepath

    def check_condition(self) -> bool:
        """Check if the current condition has been fulfilled."""
        return False
