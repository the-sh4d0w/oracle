"""Chat widget."""

import random
import typing

import rich.color
import rich.console
import rich.style
import rich.text
import textual.app
import textual.events
import textual.strip
import textual.timer
import textual.widget

import main

# FIXME: multiline? -> newline


class ChatWidget(textual.widget.Widget):
    """Chat widget."""

    dot: str = "\u25cf"

    def __init__(self, id_: str | None = None) -> None:
        """Initialize the chat widget."""
        super().__init__(id=id_)
        self.console: rich.console.Console = rich.console.Console()
        self.user_colors: dict[str, rich.color.Color] = {
            "zer0": rich.color.Color.from_rgb(255, 0, 0),
            "CR": rich.color.Color.from_rgb(0, 124, 0)
        }
        self.messages: list[tuple[str, str]] = []
        self.message_queue: list[tuple[str, str]] = []
        self.dots_shown: bool = False
        self.dot_num: int = 1
        self.dot_timer: textual.timer.Timer | None
        self.message_timer: textual.timer.Timer | None

    def dot_inc(self) -> None:
        """Increment the dot counter."""
        self.dot_num = ((self.dot_num + 1) % 3) + 1

    def message_final(self) -> None:
        """Finalise the message."""
        typing.cast(textual.timer.Timer, self.dot_timer).stop()
        self.dots_shown = False

    def _on_mount(self, event: textual.events.Mount) -> None:
        """Do stuff on mount."""
        event.stop()
        self.auto_refresh = 1 / 16

    def write_message(self, user: str, text: str) -> None:
        """Write message to the chat.

        Arguments:
            - user: the user to write the message from.
            - text: the text of the message.
        """
        if self.user_colors.get(user) is None:
            # FIXME: select better colors
            self.user_colors[user] = rich.color.Color.from_rgb(
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # use list like a FIFO queue
        self.message_queue.insert(0, (user, text))
        # add notification to chat button
        self.app: main.OracleApp
        self.app.add_notification(self.id)

    def render_line(self, y: int) -> textual.strip.Strip:
        """Render a line."""
        # setup for message from queue
        if len(self.message_queue) > 0 and not self.dots_shown:
            # FIXME: just do hardcoded delay for now
            self.dots_shown = True
            self.dot_timer = self.set_interval(0.3, self.dot_inc)
            self.message_timer = self.set_timer(2.1, self.message_final)
            self.messages.append(self.message_queue.pop())
        # show messages on screen
        if y < len(self.messages):
            user: str
            text: str
            index: int
            if len(self.messages) <= self.size.height:
                index = y
            else:
                index = y + (len(self.messages) - self.size.height)
            user, text = self.messages[index]
            if self.dots_shown and index == len(self.messages) - 1:
                result = rich.text.Text(f"({user}): {self.dot * self.dot_num}")
            else:
                result = rich.text.Text(f"({user}): {text}")
            result.stylize(rich.style.Style(color=self.user_colors[user]),
                           start=1, end=len(user) + 1)
            return textual.strip.Strip(result.render(self.console))
        return textual.strip.Strip.blank(self.size.width)
