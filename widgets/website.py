"""Website base class and some helper functions."""

import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import pathlib
import typing

import textual.app
import textual.containers
import textual.widget
import textual.widgets


def get_websites() -> list["Website"]:
    """Get all websites.

    Returns:
        All websites found.
    """
    websites: list[Website] = []
    for file in pathlib.Path("websites").iterdir():
        if file.is_file() and file.name.endswith(".py"):
            spec = typing.cast(importlib.machinery.ModuleSpec,
                               importlib.util.spec_from_file_location(
                                   file.name.removesuffix(".py"), file))
            module = importlib.util.module_from_spec(spec)
            typing.cast(importlib.abc.Loader, spec.loader).exec_module(module)
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Website):
                    # necessary to avoid error
                    websites.append(
                        obj.__call__())  # pylint:disable=unnecessary-dunder-call
    return websites


class Website(textual.widget.Widget):
    """Website widget. Mostly exists to make handling websites slightly easier."""
    website: str = "search"
    web_history: list[str] = []
    """Just a list of all visited websites."""

    def __init__(self, id_: str, title: str, keywords: list[str],
                 description: str = "This website does not provide a description.",
                 tld: str = "net") -> None:
        """Initialize the website.

        Arguments:
            - id_: the id of the website.
            - title: the title of the website.
            - keywords: the keywords to find the website by.
            - description: the description of the website.
            - tld: the top level domain of the website (default is net).
        """
        super().__init__(id=id_)
        self.id_: str = id_
        self.title: str = title
        self.domain: str = f"{self.id_}.{tld}"
        self.description: str = description
        self.keywords: list[str] = keywords

    def website_header(self) -> textual.widget.Widget:
        """Get website header.

        Arguments:
            - domain: the domain for the website header.

        Returns:
            The header widget.
        """
        return textual.containers.Horizontal(
            textual.widgets.Button("<-", id="website_button"),
            textual.widgets.Label(self.domain, id="website_label"),
            id="website_container")

    @textual.on(textual.widgets.Button.Pressed, "#website_button")
    def pressed_website_button(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle button pressed event for website_button."""
        event.stop()
        search_switcher = self.app.screen.query_one(
            "#search_switcher", textual.widgets.ContentSwitcher)
        if len(Website.web_history) > 0:
            last: str = Website.web_history.pop()
            self.app.screen.query_one("#display_inner",
                               textual.widgets.ContentSwitcher).current = last
            Website.website = last
        elif search_switcher.current == "search_page":
            self.query_one("#search_main_input", textual.widgets.Input).clear()
            search_switcher.current = "search_main"
