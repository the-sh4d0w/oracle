"""Search website."""

import typing

import textual.app
import textual.containers
import textual.events
import textual.widget
import textual.widgets

import screens.desktop
import widgets.website


class SearchWebsite(widgets.website.Website):
    """Search website."""

    def __init__(self) -> None:
        """Initialize the search website."""
        super().__init__(id_="search", title="Search", keywords=["search", "web"],
                         description="Your favourite web search engine.")

    def search(self) -> None:
        """Search the 'web'."""
        # get search term
        switcher = self.query_one("#search_switcher",
                                  textual.widgets.ContentSwitcher)
        if switcher.current == "search_main":
            search_term = self.query_one("#search_main_input",
                                         textual.widgets.Input).value
        else:
            search_term = self.query_one("#search_page_input",
                                         textual.widgets.Input).value
        # switch to page
        switcher.current = "search_page"
        self.query_one("#search_page_input",
                       textual.widgets.Input).value = search_term
        # actually do the search
        results: list[str] = []
        for website in typing.cast(screens.desktop.DesktopScreen, self.app.screen).websites:
            if not set(search_term.split()).isdisjoint(set(website.keywords)):
                results.append(f"[@click=app.link('{website.id_}')]{website.title}[/]\n"
                               f"{website.description}\n")
        # append results to page
        search_results = self.query_one(
            "#search_results", textual.widgets.RichLog)
        search_results.clear()
        if len(results) > 0:
            for result in results:
                search_results.write(result)
        else:
            search_results.write("No results found :(")

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        yield self.website_header()
        with textual.widgets.ContentSwitcher(initial="search_main", id="search_switcher"):
            yield textual.widgets.Label("literally anything else")
            with textual.containers.Container(id="search_main"):
                yield textual.widgets.Label("SEARCH", id="search_main_title")
                with textual.containers.Horizontal(id="search_box"):
                    yield textual.widgets.Input(id="search_main_input", classes="search_input")
                    yield textual.widgets.Button("⌕", id="search_icon")
            with textual.containers.Container(id="search_page"):
                with textual.containers.Horizontal(id="search_horizontal"):
                    yield textual.widgets.Button("SEARCH", id="search_page_button")
                    with textual.containers.Horizontal(id="search_box"):
                        yield textual.widgets.Input(id="search_page_input", classes="search_input")
                        yield textual.widgets.Button("⌕", id="search_icon")
                yield textual.widgets.RichLog(id="search_results", markup=True, auto_scroll=False)

    @textual.on(textual.widgets.Button.Pressed, "#search_page_button")
    def pressed_search_page_button(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle button pressed event for search_page_button."""
        event.stop()
        self.query_one("#search_main_input", textual.widgets.Input).clear()
        self.query_one("#search_switcher", textual.widgets.ContentSwitcher
                       ).current = "search_main"

    @textual.on(textual.widgets.Button.Pressed, "#search_icon")
    def pressed_search_icon(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle button pressed event for search_icon."""
        event.stop()
        self.search()

    def on_input_submitted(self, event: textual.widgets.Input.Submitted) -> None:
        """Handle input submitted event."""
        event.stop()
        self.search()
