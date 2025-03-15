"""Custom terminal widget."""

import dataclasses
import typing

import rich.console
import rich.segment
import rich.style
import rich.text
import textual.binding
import textual.events
import textual.geometry
import textual.message
import textual.reactive
import textual.scroll_view
import textual.strip
import textual.timer

import utils.command
import utils.computer
import utils.values

# TODO: scrolling?
# TODO: history
# TODO: ctrl+left and ctrl+right


class Terminal(textual.scroll_view.ScrollView, can_focus=True):
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
        textual.binding.Binding("up", "history_back",
                                "history back", show=False),
        textual.binding.Binding("down", "history_forward",
                                "history forward", show=False),
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
    history_value = textual.reactive.reactive(-1)
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
        self._lines: list[textual.strip.Strip] = []
        self._virtual_lines: list[textual.strip.Strip] = []
        self._history: list[str] = []
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

    def watch_history_value(self, history_value: int) -> None:
        """Watch the history value."""
        if history_value <= -1:
            self.history_value = -1
        elif history_value >= len(self._history):
            self.history_value = len(self._history) - 1
        if self.history_value == -1:
            self.value = ""
        else:
            self.value = self._history[self.history_value]
            # a bit cursed, but it works
            self.cursor_position = 1_000_000

    def on_resize(self, _: textual.events.Resize) -> None:
        """Do stuff on resize."""
        self._update_vlines()

    def split_strip(self, strip: textual.strip.Strip, width: int) -> list[textual.strip.Strip]:
        """Split a strip into multiple strips to fit width."""
        indices = list(range(width, (strip.cell_length // width + 1) * width, width)) \
            + [strip.cell_length]
        return list(strip.divide(indices))

    def _update_vlines(self) -> None:
        """Update virtual lines."""
        # cursed, kinda
        if self.size.width:
            self._virtual_lines = []
            for line in self._lines:
                self._virtual_lines.extend(
                    self.split_strip(line, self.size.width))
            self.virtual_size = textual.geometry.Size(
                self.size.width, len(self._virtual_lines))
            self.scroll_end(animate=False)

    def write_lines(self, lines: str) -> None:
        """Write lines."""
        console = rich.console.Console(width=1_000_000)
        for line_text in lines.split("\n"):
            line_text = line_text.format_map(utils.values.VALUES.as_dict())
            strip = textual.strip.Strip(list(console.render(line_text))[:-1])
            self._lines.append(strip)
        self._update_vlines()

    def input(self, callback: typing.Callable[..., None | str], *prompts: str) -> None:
        """Do input."""
        input_prompts: list[str] = list(prompts)
        self.write_lines(input_prompts.pop(0))
        self._input_prompts = input_prompts
        self._callback = callback

    def clear(self):
        """Clear the terminal."""
        self._lines = []
        self.virtual_size = textual.geometry.Size(
            self.size.width, len(self._virtual_lines))

    async def _on_key(self, event: textual.events.Key) -> None:
        """Do stuff on key."""
        if self.cursor_blink:
            self._blink_timer.reset()
        if event.is_printable:
            event.stop()
            self.scroll_end(animate=False)
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

    def action_history_back(self) -> None:
        """Handle history back action."""
        self.history_value += 1

    def action_history_forward(self) -> None:
        """Handle history forward action."""
        self.history_value -= 1

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
        _, scroll_y = self.scroll_offset
        y += scroll_y
        console = rich.console.Console(width=1_000_000)
        if y < len(self._virtual_lines):
            if y == len(self._virtual_lines) - 1:
                value = rich.text.Text(self.value + " ")
                if self.cursor_visible and self.has_focus:
                    value.stylize(rich.style.Style(color="white", bgcolor="black", reverse=True),
                                  self.cursor_position, self.cursor_position + 1)
                input_segments = list(value.render(console))
                if len(self._virtual_lines) > 0:
                    return textual.strip.Strip([*self._virtual_lines[-1], *input_segments])
                return textual.strip.Strip(input_segments)
            return textual.strip.Strip(self._virtual_lines[y])
        return textual.strip.Strip.blank(self.size.width)

    def on_terminal_submitted(self, event: Submitted) -> None:
        """Handle terminal submit event."""
        # still a bit cursed, but it could be so much worse
        event.stop()
        console = rich.console.Console(width=1_000_000)
        self.history_value = -1
        self._history.insert(0, event.value)
        # FIXME: improve
        self._lines[-1]._segments.extend(
            [*rich.text.Text(event.value).render(console)])
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
