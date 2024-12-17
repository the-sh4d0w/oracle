"""Custom terminal widget."""

import dataclasses
import typing

import rich.console
import rich.segment
import rich.style
import rich.text
import textual.binding
import textual.events
import textual.message
import textual.reactive
import textual.strip
import textual.timer
import textual.widget

import utils.command
import utils.computer
import utils.values

# TODO: scrolling?
# TODO: history
# TODO: ctrl+left and ctrl+right


class Terminal(textual.widget.Widget, can_focus=True):
    """Custom terminal widget."""
    # inspired by textual.widgets.Input

    BINDINGS = [
        textual.binding.Binding("left", "cursor_left",
                                "cursor left", show=False),
        textual.binding.Binding("ctrl+left", "cursor_left_word",
                                "cursor left word", show=False),
        textual.binding.Binding("right", "cursor_right",
                                "cursor right", show=False),
        textual.binding.Binding("ctrl+right", "cursor_right_word",
                                "cursor right word", show=False),
        textual.binding.Binding("enter", "submit",
                                "submit", show=False),
        textual.binding.Binding("backspace", "delete_left",
                                "delete left", show=False),
        textual.binding.Binding("delete", "delete_right",
                                "delete right", show=False)
    ]

    prompts = textual.reactive.reactive([])
    value = textual.reactive.reactive("", always_update=True)
    cursor_position = textual.reactive.reactive(0)
    cursor_blink = textual.reactive.reactive(True, init=False)
    cursor_visible = textual.reactive.reactive(True)
    TERMINAL: "Terminal"

    @dataclasses.dataclass
    class Submitted(textual.message.Message):
        """Submitted event message."""
        terminal: "Terminal"
        value: str

        @property
        def control(self) -> "Terminal":
            """Alias for self.terminal."""
            return self.terminal

    def __init__(self, id_: str | None = None) -> None:
        """Initialize the terminal."""
        super().__init__(id=id_)
        self._blink_timer: textual.timer.Timer
        self._lines: list[list[rich.segment.Segment]] = []
        # variable for command input handling
        self._input_prompts: list[str] = []
        self._outputs: list[str] = []
        self._callback: typing.Callable[[str], None | str] | None = None
        # reference to self for commands
        Terminal.TERMINAL = self
        # add first prompt
        self.write_lines(utils.computer.NETWORK.computer.prompt)

    def watch_value(self, value: str) -> None:
        """Watch the value."""
        if self.cursor_position <= 0:
            self.cursor_position = 0
        elif self.cursor_position >= len(value):
            self.cursor_position = len(value)

    def watch_cursor_position(self, cursor_position: int) -> None:
        """Watch the cursor position."""
        if cursor_position <= 0:
            self.cursor_position = 0
        elif cursor_position >= len(self.value):
            self.cursor_position = len(self.value)

    def write_lines(self, lines: str) -> None:
        """Write lines."""
        for line in lines.split("\n"):
            line = line.format_map(utils.values.VALUES.as_dict())
            line = list(rich.console.Console().render(line))[:-1]
            self._lines.append(line)

    def input(self, callback: typing.Callable[..., None | str], *prompts: str) -> None:
        """Do input."""
        input_prompts: list[str] = list(prompts)
        self.write_lines(input_prompts.pop(0))
        self._input_prompts = input_prompts
        self._callback = callback

    def clear(self):
        """Clear the terminal."""
        self._lines = []

    async def _on_key(self, event: textual.events.Key) -> None:
        if self.cursor_blink:
            self._blink_timer.reset()
        if event.is_printable:
            event.stop()
            assert event.character is not None
            if self.cursor_position >= len(self.value):
                self.value += event.character
                self.cursor_position = len(self.value)
            else:
                self.value = self.value[:self.cursor_position] + \
                    event.character + self.value[self.cursor_position:]
                self.cursor_position += 1
            event.prevent_default()

    def _on_focus(self, event: textual.events.Focus) -> None:
        """Do stuff on focus."""
        event.stop()
        self.cursor_position = len(self.value)
        if self.cursor_blink:
            self._blink_timer.resume()

    def action_cursor_left(self) -> None:
        """Handle cursor left action."""
        self.cursor_position -= 1

    def action_cursor_right(self) -> None:
        """Handle cursor right action."""
        self.cursor_position += 1

    def action_submit(self) -> None:
        """Handle submit action."""
        self.post_message(self.Submitted(self, self.value))
        self.value = ""

    def action_delete_left(self) -> None:
        """Handle delete left action."""
        if self.cursor_position == 0:
            return
        self.value = self.value[:self.cursor_position - 1] + \
            self.value[self.cursor_position:]
        if self.cursor_position != len(self.value):
            self.cursor_position -= 1

    def action_delete_right(self) -> None:
        """Handle delete left action."""
        self.value = self.value[:self.cursor_position] + \
            self.value[self.cursor_position + 1:]

    def toggle_cursor(self) -> None:
        """Toggle visibility of cursor."""
        self.cursor_visible = not self.cursor_visible

    def _on_mount(self, event: textual.events.Mount) -> None:
        """Do stuff on mount."""
        event.stop()
        self._blink_timer = self.set_interval(
            0.5, self.toggle_cursor, pause=not (self.cursor_blink and self.has_focus))

    def render_line(self, y: int) -> textual.strip.Strip:
        """Render a line."""
        console = rich.console.Console()
        if y == self.size.height - 1:
            value = rich.text.Text(self.value + " ")
            if self.cursor_visible and self.has_focus:
                value.stylize(rich.style.Style(color="white", bgcolor="black", reverse=True),
                              self.cursor_position, self.cursor_position + 1)
            input_segments = list(value.render(console))
            if len(self._lines) > 0:
                return textual.strip.Strip([*self._lines[-1], *input_segments])
            return textual.strip.Strip(input_segments)
        if y >= (self.size.height - len(self._lines)):
            return textual.strip.Strip(self._lines[y - self.size.height])
        return textual.strip.Strip.blank(self.size.width)

    def on_terminal_submitted(self, event: Submitted) -> None:
        """Handle terminal submit event."""
        # still a bit curse, but it could be so much worse
        event.stop()
        self._lines[-1] += [*rich.text.Text(event.value
                                            ).render(rich.console.Console())]
        if self._callback:
            self._outputs.append(event.value)
            if len(self._input_prompts) == 0:
                if (output := self._callback(*self._outputs)):
                    self.write_lines(output)
                self._outputs = []
                self._callback = None
            else:
                self.write_lines(self._input_prompts.pop(0))
        elif event.value:
            if (output := utils.command.parse(event.value)):
                self.write_lines(output)
        if not self._callback:
            self.write_lines(utils.computer.NETWORK.computer.prompt)
