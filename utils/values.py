"""Value stuff."""

import dataclasses

import utils.command

# FIXME: improve this; make value gathering easier, more obvious, and central


@dataclasses.dataclass
class Values:
    """Values and colors for text formatting."""
    player: str | None
    user: str | None
    name: str | None
    path: str | None

    @classmethod
    def default(cls) -> "Values":
        """Create Values with None values."""
        return cls(None, None, None, None)

    def as_dict(self) -> dict[str, str]:
        """Values as a dictionary."""
        return {**dataclasses.asdict(self), **utils.command.ORACLE.get_css_variables()}


VALUES = Values.default()
