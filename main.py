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

import utils.command
import utils.computer
import utils.themes
import screens.boot
import screens.login
import screens.desktop
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
    ENABLE_COMMAND_PALETTE = False
    # load all styles from /styles
    CSS_PATH = list(pathlib.Path("styles").iterdir())
    BINDINGS = [
        textual.binding.Binding("f2", "screenshot",
                                "Take a screenshot.", show=False)
    ]

    do_input = textual.reactive.reactive(False, init=False)
    # need to initialize them here due to __init__ of App calling get_css_variables
    # FIXME: temp theme choice for now
    theme: str | None = "purple"
    themes: dict[str, textual.design.ColorSystem] = utils.themes.get_themes()

    def __init__(self, no_boot: bool = False, debug: bool = False) -> None:
        """Initialize the oracle app.

        Arguments:
            - no_boot: skips boot screen if True.
            - debug: adds debug menu if True.
        """
        super().__init__()
        # terminal stuff
        self._last_prompt: str | None = None
        self._last_big_prompt: str | None = None
        self._prompts: list[str] = []
        self._output: list[str] = []
        self._func: typing.Callable[..., str | None]
        # debug / dev flags
        self._no_boot: bool = no_boot
        self._debug: bool = debug
        # network, computer and filesystem stuff
        self.network = utils.computer.Network()
        # needed so that commands can access OracleApp (e.g. for input)
        self.commands = utils.command.get_commands(self._debug)
        utils.command.ORACLE = self

    def get_css_variables(self) -> dict[str, str]:
        """Get color variables for css.

        Returns:
            The variables?
        """
        # inspired by https://github.com/darrenburns/posting
        theme: dict[str, str] = {}
        if self.theme:
            system: textual.design.ColorSystem | None \
                = self.themes.get(self.theme)
            if system:
                theme = system.generate()
        return {**super().get_css_variables(), **theme}

    def watch_do_input(self, value: bool) -> None:
        """Watch the input."""
        # *sigh*; needed for logout
        if self.screen.id == "desktop":
            terminal = self.query_one("#terminal", widgets.terminal.Terminal)
            if value:
                if self._last_prompt is None:
                    self._last_prompt = terminal.prompt
                if self._last_big_prompt is None:
                    self._last_big_prompt = terminal.big_prompt
            else:
                terminal.prompt = typing.cast(str, self._last_prompt)
                terminal.big_prompt = self._last_big_prompt
                self._last_prompt = None
                self._last_big_prompt = None

    def on_mount(self) -> None:
        """Do stuff on mount."""
        self.install_screen(screens.desktop.DesktopScreen(), "desktop")
        self.install_screen(screens.login.LoginScreen(), "login")
        self.install_screen(screens.boot.BootScreen(), "boot")
        self.push_screen("login")
        if not self._no_boot:
            self.push_screen("boot")

    def action_link(self, target: str) -> None:
        """Handle link action."""
        # taken from Website.switch_website
        display: textual.widgets.ContentSwitcher = self.query_one(
            "#display_inner", textual.widgets.ContentSwitcher)
        widgets.website.Website.web_history.append(
            typing.cast(str, display.current))
        display.current = target
        widgets.website.Website.website = target

    def on_terminal_submitted(self, event: widgets.terminal.Terminal.Submitted) -> None:
        """Handle terminal submit event."""
        # slightly cursed
        terminal = self.query_one("#terminal", widgets.terminal.Terminal)
        if self.do_input:
            # handle input for commands
            self._output.append(event.value)
        else:
            # parse terminal input
            if len(event.value) > 0:
                output = utils.command.parse(self, event.value)
            else:
                output = None
        # actually call the function if all inputs have been gathered
        if self.do_input and len(self._prompts) == 0:
            output = self._func(*self._output)
            self._output = []
            self.do_input = False
        elif self.do_input:
            output = None
        # write to display
        if output is not None:
            for line in output.split("\n"):
                terminal.write_line(line)
        # update the prompt
        if self.do_input and len(self._prompts) > 0:
            terminal.prompt = self._prompts[0]
            terminal.big_prompt = None
            self._prompts = self._prompts[1:]

    def input(self, func: typing.Callable[..., str | None], prompts: list[str]) -> None:
        """Set input stuff.

        Arguments:
            - func: the function to call with the input.
            - prompts: the prompts to use.
        """
        # FIXME: improve this!
        if len(prompts) > 0:
            self.do_input = True
            self._func = func
            self._prompts = prompts

    def add_notification(self, widget_id) -> None:
        """Add notification to button.

        Arguments:
            - widget_id: the id of the widget to add a notification for (should be own id).
        """
        self.query_one("#desktop",
                       screens.desktop.DesktopScreen).add_notification(widget_id)


@click.command()
@click.option("-b", "--noboot", is_flag=True, help="Start without bootscreen.")
@click.option("-d", "--debug", is_flag=True, help="Add a debug menu.")
def main(noboot: bool = False, debug: bool = False) -> None:
    """The oracle game."""
    OracleApp(no_boot=noboot, debug=debug).run()


if __name__ == "__main__":
    main()
