"""Boot screen."""

import pathlib
import random
import time
import typing

import textual.app
import textual.containers
import textual.screen
import textual.timer
import textual.widgets


class BootScreen(textual.screen.Screen):
    """Boot screen."""

    def __init__(self) -> None:
        """Initialize the boot screen."""
        super().__init__()
        with pathlib.Path("boot.txt").open("r", encoding="utf-8") as file:
            self.lines: list[str] = file.read().split("\n")
        self.index: int = 0
        self.timer: textual.timer.Timer | None = None

    def next(self) -> None:
        """Add lines of text."""
        if self.index < len(self.lines):
            time.sleep(random.uniform(0, 0.5))
            boot_container = self.query_one(
                "#boot_container", textual.containers.VerticalScroll)
            boot_container.mount(textual.widgets.Label(self.lines[self.index]))
            boot_container.scroll_end(animate=False)
            self.index += 1
        else:
            time.sleep(3)
            typing.cast(textual.timer.Timer, self.timer).stop()
            self.app.pop_screen()

    def on_mount(self) -> None:
        """Do stuff on mount."""
        self.timer = self.set_interval(0.5, self.next)

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        yield textual.containers.VerticalScroll(id="boot_container")
