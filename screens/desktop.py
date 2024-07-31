"""Main screen."""

import textual.app
import textual.containers
import textual.screen
import textual.widgets

import utils
import utils.command
import widgets.chat
import widgets.terminal
import widgets.website

# TODO: improve
# ui things: terminal✔; web browser✔; emails; chat program✔; news!; notes (somewhat)
# websites: search engine; wiki; social media; stock market; gambling


class DesktopScreen(textual.screen.Screen):
    """Main screen."""

    def __init__(self) -> None:
        """Initialize the desktop screen."""
        super().__init__(id="desktop")
        self.websites: list[widgets.website.Website] \
            = widgets.website.get_websites()

    def on_mount(self) -> None:
        """Do stuff on mount."""
        utils.command.TERMINAL = self.query_one(
            "#terminal", widgets.terminal.Terminal)

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        with textual.containers.Horizontal():
            with textual.containers.Vertical(id="display"):
                with textual.containers.Horizontal(id="display_buttons"):
                    yield textual.widgets.Button("web browser", id="web_browser_button",
                                                 classes="display_button display_button_active")
                    yield textual.widgets.Button("emails", id="emails_button",
                                                 classes="display_button")
                    yield textual.widgets.Button("chat", id="chat_button",
                                                 classes="display_button")
                    yield textual.widgets.Button("news", id="news_button",
                                                 classes="display_button")
                    yield textual.widgets.Button("notes", id="notes_button",
                                                 classes="display_button")
                # can't use two ContentSwitcher (directly together?), so this has to do
                with textual.widgets.ContentSwitcher(initial="search", id="display_inner"):
                    # cursed (like everything else), but it works
                    yield from self.websites
                    yield textual.widgets.ListView(id="emails")
                    yield widgets.chat.ChatWidget(id_="chat")
                    yield textual.widgets.ListView(id="news")
                    yield textual.widgets.TextArea(tab_behavior="indent",
                                                   show_line_numbers=True, id="notes")
            yield widgets.terminal.Terminal(id_="terminal")

    @textual.on(textual.widgets.Button.Pressed, ".display_button")
    def pressed_display_button(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle button pressed event for display_button."""
        # cursed, like everything else
        event.stop()
        display_inner = self.query_one(
            "#display_inner", textual.widgets.ContentSwitcher)
        # change active button
        self.query_one(".display_button_active", textual.widgets.Button
                       ).remove_class("display_button_active")
        new_button = self.query_one(f"#{event.button.id}.display_button",
                                    textual.widgets.Button)
        new_button.remove_class("display_button_notification")
        new_button.add_class("display_button_active")
        # change display
        if event.button.id == "web_browser_button":
            display_inner.current = widgets.website.Website.website
        else:
            display_inner.current = str(
                event.button.id).removesuffix("_button")
