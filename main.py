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
import utils.computer
import utils.shared
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

__VERSION__ = 0, 2, 1
"""Game version as Major.Minor.Patch (semantic versioning)."""


class OracleApp(textual.app.App):
    """Oracle app."""
    # load all styles from styles/
    CSS_PATH = list(pathlib.Path("styles").iterdir())

    def on_mount(self) -> None:
        """Do stuff on mount."""
        self.push_screen(screens.login.LoginScreen())
        if not utils.values.GAME_VALUES.noboot:
            self.push_screen(screens.boot.BootScreen())

    def action_link(self, target: str) -> None:
        """Handle link action."""
        # taken from Website.switch_website
        display: textual.widgets.ContentSwitcher = self.screen.query_one(
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
        typing.cast(screens.desktop.DesktopScreen,
                    self.app.screen).add_notification(widget_id)


@click.command()
@click.option("-b", "--noboot", is_flag=True, help="Start without bootscreen.")
@click.option("-d", "--debug", is_flag=True, help="Add a debug menu.")
def main(noboot: bool = False, debug: bool = False) -> None:
    """The oracle game."""
    # set debug/dev variables
    utils.values.GAME_VALUES.noboot = noboot
    utils.values.GAME_VALUES.debug = debug
    OracleApp.ENABLE_COMMAND_PALETTE = debug
    OracleApp().run()


if __name__ == "__main__":
    main()
