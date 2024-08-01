"""Custom terminal widget."""

import dataclasses

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

# TODO: scrolling?
# TODO: history
# TODO: ctrl+left and ctrl+right
# FIXME: remove not needed stuff


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

    big_prompt: textual.reactive.reactive[str |
                                          None] = textual.reactive.reactive(None)
    prompt = textual.reactive.reactive("[blue]└──$[/] ")
    value = textual.reactive.reactive("", always_update=True)
    cursor_position = textual.reactive.reactive(0)
    cursor_blink = textual.reactive.reactive(True, init=False)
    cursor_visible = textual.reactive.reactive(True)

    @dataclasses.dataclass
    class Submitted(textual.message.Message):
        """Submitted event message."""
        terminal: "Terminal"
        value: str

        @property
        def control(self) -> "Terminal":
            """Alias for self.terminal."""
            return self.terminal

    def __init__(self, id_: str | None = None, classes: str | None = None) -> None:
        """Initialize the terminal."""
        super().__init__(id=id_, classes=classes)
        self._prompt_segments: list[rich.segment.Segment]
        self._input_segments: list[rich.segment.Segment]
        self._blink_timer: textual.timer.Timer
        self._lines: list[list[rich.segment.Segment]] = []
        self._input: bool = False
        """Used for non-standard input. True supresses the Submitted event."""
        # set correct theme color
        color: str = self.app.get_css_variables()["primary"]
        self.big_prompt = f"[{color}]┌([#00FF00]sh4d0w[/]@[#D2691E]" \
            "oracle[/])-([#FF0000]~[/])[/]"
        self.prompt = f"[{color}]└──$[/] "

    def watch_prompt(self, prompt: str) -> None:
        """Watch the prompt."""
        self._prompt_segments = list(
            rich.console.Console().render(prompt))[:-1]

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

    def write_line(self, line: str | list[rich.segment.Segment]) -> None:
        """Write a line."""
        if isinstance(line, str):
            self._lines.append(list(rich.console.Console().render(line))[:-1])
        elif isinstance(line, list):
            self._lines.append(line)

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

    def _on_focus(self, _: textual.events.Focus) -> None:
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
        if self.big_prompt is not None:
            self.write_line(
                list(rich.console.Console().render(self.big_prompt))[:-1])
        self.write_line([*self._prompt_segments,
                         rich.segment.Segment(self.value)])
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

    def _on_mount(self) -> None:  # pylint:disable=arguments-differ
        """Do stuff on mount."""
        self._blink_timer = self.set_interval(0.5, self.toggle_cursor,
                                              pause=not (self.cursor_blink and self.has_focus))

    def render_line(self, y: int) -> textual.strip.Strip:
        """Render a line."""
        if y == self.size.height - 1:
            result = rich.text.Text(self.value + " ")
            if self.cursor_visible and self.has_focus:
                result.stylize(rich.style.Style(color="white", bgcolor="black", reverse=True),
                               self.cursor_position, self.cursor_position + 1)
            self._input_segments = list(result.render(rich.console.Console()))
            return textual.strip.Strip([*self._prompt_segments, *self._input_segments])
        if self.big_prompt is not None and y == self.size.height - 2:
            return textual.strip.Strip(list(rich.console.Console().render(self.big_prompt))[:-1])
        if self.big_prompt is not None and y >= (self.size.height - len(self._lines) - 2):
            return textual.strip.Strip(self._lines[y - self.size.height + 2])
        if y >= (self.size.height - len(self._lines) - 1):
            return textual.strip.Strip(self._lines[y - self.size.height + 1])
        return textual.strip.Strip.blank(self.size.width)

    def clear(self):
        """Clear the terminal."""
        self._lines = []
