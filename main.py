"""Main code for the oracle game prototype."""

import pathlib
import sys
import typing

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
import widgets.chat
import widgets.terminal
import widgets.website

# TODO:
# ☐ logging
# ☐ full docstrings
# ☐ full type hinting
# ☐ replace list with set? -> websites or what?
# 🗹 make list

# make all of this better
# TODO: mostly improve commands
# TODO: and add file system/computers
# TODO: themes, why not?


class Command:
    """Command for the terminal."""

    COMMANDS: list["Command"] = []
    arguments: list[str] = []
    terminal: widgets.terminal.Terminal
    oracle: "OracleApp"

    def __init__(self, name: str, help_text: str) -> None:
        """Initialize the command."""
        self.name: str = name
        self.help_text: str = help_text

    def run(self) -> str | None:
        """Run method, has to be replaced."""
        raise NotImplementedError()

    @classmethod
    def create_complex_command(cls) -> typing.Callable:
        """Create a complex command. Takes arguments."""
        def __command(func: typing.Callable[[list[str], str | None]]) -> "Command":
            command = Command(func.__name__.removesuffix("_"),
                              "" if func.__doc__ is None else func.__doc__)
            command.run = lambda: "TODO: complex commands"
            cls.COMMANDS.append(command)
            return command
        return __command

    @classmethod
    def create_simple_command(cls) -> typing.Callable:
        """Create a simple command. Takes no additional arguments."""
        def __command(func: typing.Callable[[], str | None]) -> "Command":
            command = Command(func.__name__.removesuffix("_"),
                              "" if func.__doc__ is None else func.__doc__)
            command.run = func
            cls.COMMANDS.append(command)
            return command
        return __command


@Command.create_simple_command()
def neofetch() -> str:
    """Display system information."""
    # not here; need icon/logo
    return r"""
$$$$$$$$$\                              $$\
$$  ___$$ |                             $$ |
$$ |   $$ | $$$$$$$\ $$$$$$\   $$$$$$$\ $$ | $$$$$$\
$$ |   $$ |$$  _____|\____$$\ $$  _____|$$ |$$  __$$\
$$ |   $$ |$$ |      $$$$$$$ |$$ |      $$ |$$$$$$$$ |
$$ |   $$ |$$ |     $$  __$$ |$$ |      $$ |$$   ____|
$$$$$$$$$ |$$ |     \$$$$$$$ |\$$$$$$$\ $$ |\$$$$$$$\
\_________|\__|      \_______| \_______|\__| \_______|
"""


@Command.create_simple_command()
def help_() -> str:
    """Show a list of all commands."""
    return "\n".join([f"{command.name:10} {command.help_text}"
                      for command in Command.COMMANDS])


def logout_confirm(answer: str) -> None:
    """Check if player actually wants to log out."""
    if answer.lower() in ("y", "yes"):
        Command.terminal.app.pop_screen()
        Command.terminal.app.uninstall_screen("desktop")
        Command.terminal.app.install_screen(
            screens.desktop.DesktopScreen(), "desktop")


@Command.create_simple_command()
def logout_() -> None:
    """Log out."""
    Command.oracle.input(logout_confirm, ["Do you want to log out? (y/N) "])


@Command.create_simple_command()
def exit_() -> None:
    """Exit the current computer."""
    # TODO: implement exit


@Command.create_simple_command()
def clear() -> None:
    """Clear the terminal."""
    Command.terminal.clear()


@Command.create_simple_command()
def ls() -> str:
    """List files and directories."""
    # TODO: implement list directory
    return "TODO: ls"


@Command.create_simple_command()
def cd() -> None:
    """Change directory."""
    # TODO: implement changing directory


def login_verify(user: str, pwd: str) -> str:
    """Verify login."""
    if user == pwd == "admin":
        return "Sucessfully logged in!"
    return "Wrong username or password."


@Command.create_simple_command()
def login() -> str:
    """Login to the computer."""
    Command.oracle.input(login_verify, ["user: ", "pwd: "])
    return "LOGIN STUFF"


@Command.create_simple_command()
def chat() -> str:
    """Do a chat test."""
    chat_widget = Command.oracle.query_one("#chat", widgets.chat.ChatWidget)
    for i in range(int(Command.arguments[0])):
        chat_widget.write_message("zer0", f"{i} Lorem ipsum, dolor sit amet.")
    return "sent test message"

# FIXME: arguments; technically they work


class OracleApp(textual.app.App):
    """Oracle app."""
    ENABLE_COMMAND_PALETTE = False
    # load all styles from /styles
    CSS_PATH = list(pathlib.Path("styles").iterdir())
    BINDINGS = [
        textual.binding.Binding("f2", "screenshot",
                                "Take a screenshot.", show=False)
    ]

    user = textual.reactive.reactive("user")
    computer = textual.reactive.reactive("computer")
    path = textual.reactive.reactive("~")
    do_input = textual.reactive.reactive(False, init=False)
    # need to initialize them here due to how the __init__ of App works
    theme: str | None = None
    themes: dict[str, textual.design.ColorSystem] = {}

    def __init__(self, no_boot: bool = False) -> None:
        """Initialize the oracle app.

        Arguments:
            - no_boot: skips boot screen if True.
        """
        super().__init__()
        self._last_prompt: str | None = None
        self._last_big_prompt: str | None = None
        self._prompts: list[str] = []
        self._output: list[str] = []
        self._func: typing.Callable[..., str | None]
        self._no_boot: bool = no_boot
        # needed so that Command can access OracleApp (e.g. for input)
        # FIXME: make it better
        Command.oracle = self

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

    def _watch_do_input(self, value: bool) -> None:
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

    def parse(self, command_name: str, arguments: list[str]) -> str | None:
        """Parse the command and return output.

        Arguments:
            - command_name: the command to parse for.
            - arguments: arguments supplied.

        Returns:
            The output of the command.
        """
        Command.terminal = self.query_one(
            "#terminal", widgets.terminal.Terminal)
        Command.arguments = arguments
        for command in Command.COMMANDS:
            if command_name == command.name:
                return command.run()
        return f"Error: {command_name} is not a known command."

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
            values = event.value.split()
            if len(values) > 0:
                output = self.parse(values[0], values[1:])
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


if __name__ == "__main__":
    OracleApp("-b" in sys.argv or "--noboot" in sys.argv).run()
