"""Main code for the oracle game prototype."""

import pathlib
import typing

import click
import textual.app
import textual.binding
import textual.containers
import textual.design
import textual.events
import textual.message
import textual.reactive
import textual.screen
import textual.strip
import textual.timer
import textual.widget
import textual.widgets

import screens.boot
import screens.login
import screens.desktop
import utils.command
import utils.computer
import utils.themes
import utils.values
import widgets.chat
import widgets.terminal
import widgets.website

# TODO:
# ☐ logging
# ☐ full docstrings
# ☐ full type hinting
# 🗹 make list

# make all of this better
# TODO: config/settings?
# FIXME: maybe add some useful methods to wrap calls to other functions


class OracleApp(textual.app.App):
    """Oracle app."""
    if not utils.values.GAME_VALUES.debug:
        ENABLE_COMMAND_PALETTE = False
    # load all styles from /styles
    CSS_PATH = list(pathlib.Path("styles").iterdir())
    BINDINGS = [
        textual.binding.Binding("f2", "screenshot",
                                "Take a screenshot.", show=False)
    ]

    def __init__(self, no_boot: bool = False) -> None:
        """Initialize the oracle app.

        Arguments:
            - no_boot: skips boot screen if True.
            - debug: adds debug menu if True.
        """
        super().__init__()
        # debug / dev flags
        self._no_boot: bool = no_boot

    def on_mount(self) -> None:
        """Do stuff on mount."""
        self.push_screen(screens.login.LoginScreen())
        if not self._no_boot:
            self.push_screen(screens.boot.BootScreen())

    def action_link(self, target: str) -> None:
        """Handle link action."""
        # taken from Website.switch_website
        display: textual.widgets.ContentSwitcher = self.query_one(
            "#display_inner", textual.widgets.ContentSwitcher)
        widgets.website.Website.web_history.append(
            typing.cast(str, display.current))
        display.current = target
        widgets.website.Website.website = target

    def add_notification(self, widget_id) -> None:
        """Add notification to button.

        Arguments:
            - widget_id: the id of the widget to add a notification for (should be own id).
        """
        self.query_one("#desktop", screens.desktop.DesktopScreen
                       ).add_notification(widget_id)


@click.command()
@click.option("-b", "--noboot", is_flag=True, help="Start without bootscreen.")
@click.option("-d", "--debug", is_flag=True, help="Add a debug menu.")
def main(noboot: bool = False, debug: bool = False) -> None:
    """The oracle game."""
    utils.values.GAME_VALUES.debug = debug
    OracleApp(no_boot=noboot).run()


if __name__ == "__main__":
    main()
