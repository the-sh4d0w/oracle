"""Main screen."""

import textual.app
import textual.containers
import textual.css
import textual.css.query
import textual.screen
import textual.widgets

import utils
import utils.command
import utils.values
import widgets.chat
import widgets.debug
import widgets.terminal
import widgets.website


class DesktopScreen(textual.screen.Screen):
    """Main screen."""

    def __init__(self) -> None:
        """Initialize the desktop screen."""
        super().__init__(id="desktop")
        self.websites: list[widgets.website.Website] \
            = widgets.website.get_websites()
        self.active_id: str = "web_browser"

    def on_mount(self) -> None:
        """Do stuff on mount."""
        # FIXME: whyyyyy?
        utils.command.COMMANDS = utils.command.get_commands()
        widgets.terminal.Terminal.TERMINAL.focus()

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        with textual.containers.Horizontal():
            with textual.containers.Vertical(id="display"):
                with textual.containers.Horizontal(id="display_buttons"):
                    yield textual.widgets.Button("NetBrowser", id="web_browser_button",
                                                 classes="display_button display_button_active")
                    yield textual.widgets.Button("NetMail", id="netmail_button",
                                                 classes="display_button")
                    yield textual.widgets.Button("chat", id="chat_button",
                                                 classes="display_button")
                    yield textual.widgets.Button("news", id="news_button",
                                                 classes="display_button")
                    yield textual.widgets.Button("notes", id="notes_button",
                                                 classes="display_button")
                    if utils.values.GAME_VALUES.debug:  # pylint:disable=protected-access
                        yield textual.widgets.Button("debug", id="debug_button",
                                                     classes="display_button")
                # can't use two ContentSwitcher (directly together?), so this has to do
                with textual.widgets.ContentSwitcher(initial="search", id="display_inner"):
                    # cursed (like everything else), but it works
                    yield from self.websites
                    yield textual.widgets.ListView(id="netmail")
                    yield widgets.chat.ChatWidget(id_="chat")
                    yield textual.widgets.ListView(id="news")
                    yield textual.widgets.TextArea(tab_behavior="indent",
                                                   show_line_numbers=True, id="notes")
                    yield widgets.debug.DebugWidget(id_="debug")
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
        # set active id for notifications
        self.active_id = str(event.button.id).removesuffix("_button")
        # change display
        if event.button.id == "web_browser_button":
            display_inner.current = widgets.website.Website.website
        else:
            display_inner.current = self.active_id

    def add_notification(self, widget_id: str) -> None:
        """Add notification to button and create toast.

        Arguments:
            - widget_id: the id of the widget to add a notification for (should be own id).
        """
        try:
            widget_button = self.query_one(f"#{widget_id}_button",
                                           textual.widgets.Button)
            if "display_button_notification" not in widget_button.classes \
                    and self.active_id != widget_id:
                widget_button.add_class("display_button_notification")
                self.app.notify(f"new {widget_button.label} message")
        except textual.css.query.NoMatches:
            pass
