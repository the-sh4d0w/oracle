"""Themes utilities."""

import json
import pathlib
import typing

import textual.design

THEME_PATH = "themes.json"

# TODO: maybe implement custom variables?


def get_themes() -> dict[str, textual.design.ColorSystem]:
    """Get all themes.

    Returns:
        The themes.
    """
    results: dict[str, textual.design.ColorSystem] = {}
    colors: list[dict[str, typing.Any]] = json.loads(
        pathlib.Path(THEME_PATH).read_text("utf-8"))
    for color in colors:
        color_name: str = color["name"]
        # don't need the name for the color system
        color.pop("name")
        # all have to be darkmode (otherwise we get white backgrounds)
        results[color_name] = textual.design.ColorSystem(**color, dark=True)
    return results
