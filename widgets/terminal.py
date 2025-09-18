"""Custom terminal widget."""

import asyncio
import copy
import dataclasses
import re

import rich.console
import rich.text
import textual.binding
import textual.events
import textual.geometry
import textual.message
import textual.reactive
import textual.scroll_view
import textual.strip
import textual.theme
import textual.timer

import utils.command
import utils.network
import utils.values

# TODO: pause terminal input while executing command to prevent entering additional text
# TODO: improve performance
# TODO: ctrl+left and ctrl+right


class Terminal(textual.scroll_view.ScrollView, can_focus=True):
    """Custom terminal widget."""

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
        textual.binding.Binding("tab", "complete",
                                "complete command", show=False),
        textual.binding.Binding("enter", "submit",
                                "submit", show=False),
        textual.binding.Binding("backspace", "delete_left",
                                "delete left", show=False),
        textual.binding.Binding("delete", "delete_right",
                                "delete right", show=False)
    ]

    value = textual.reactive.reactive("", always_update=True)
    cursor_position = textual.reactive.reactive(0)
    cursor_blink = textual.reactive.reactive(True, init=False)
    cursor_visible = textual.reactive.reactive(True)
    history_value = textual.reactive.reactive(-1)
    cache_valid = textual.reactive.reactive(True)
    TERMINAL: "Terminal"

    @dataclasses.dataclass
    class Submitted(textual.message.Message):
        """Submitted event message."""
        terminal: "Terminal"
        value: str

    def __init__(self, id_: str | None = None) -> None:
        """Initialize the terminal."""
        super().__init__(id=id_)
        self._render_console: rich.console.Console = rich.console.Console(
            highlight=False)
        self._blink_timer: textual.timer.Timer
        self._lines: list[str] = []
        # cache of rendered lines: rendered Strip, line index, type?
        self._lines_cache: list[textual.strip.Strip] = []
        self._history: list[str] = []
        # variables for command input handling
        self._input_event: asyncio.Event = asyncio.Event()
        self._input_event.set()
        self._input: str = ""
        # reference to self for commands
        Terminal.TERMINAL = self

    def _replace_variables(self, text: str) -> str:
        """Replace variables with values, both game and theme variables (e.g. $primary)."""
        return re.sub(r"\[\$([a-zA-Z\-]+)\]", r"[{\1}]", text).format_map(
            self.app.get_css_variables() | utils.values.VALUES.as_dict())

    def _update_cache(self) -> None:
        """Update cache of rendered lines."""
        self._lines_cache.clear()
        lines: list[str] = copy.copy(self._lines)
        if len(lines) > 0:
            lines[-1] += self.value
        for line_text in lines:
            line_text = self._replace_variables(line_text)
            text: rich.text.Text = self._render_console.render_str(line_text)
            for line in text.divide(range(self._render_console.width, text.cell_len,
                                    self._render_console.width)):
                self._lines_cache.append(textual.strip.Strip(
                    line.render(self._render_console)))
        self.virtual_size = textual.geometry.Size(self.size.width,
                                                  len(self._lines_cache))

    def _on_focus(self, event: textual.events.Focus) -> None:
        """Do stuff on focus."""
        event.stop()
        self.cursor_position = len(self.value)
        if self.cursor_blink:
            self._blink_timer.resume()

    def _on_mount(self, event: textual.events.Mount) -> None:
        """Do stuff on mount."""
        event.stop()
        self._blink_timer = self.set_interval(
            0.5, self.toggle_cursor, pause=not (self.cursor_blink and self.has_focus))
        self.app.theme_changed_signal.subscribe(self, self.on_theme_change)
        self.write_lines(utils.network.NETWORK.computer.prompt)

    async def _on_key(self, event: textual.events.Key) -> None:
        """Do stuff on key."""
        if self.cursor_blink:
            self._blink_timer.reset()
        if event.is_printable:
            event.stop()
            self.scroll_end(animate=False, immediate=True, force=True)
            assert event.character is not None
            if self.cursor_position >= len(self.value):
                self.value += event.character
                self.cursor_position = len(self.value)
            else:
                self.value = self.value[:self.cursor_position] + \
                    event.character + self.value[self.cursor_position:]
                self.cursor_position += 1
            event.prevent_default()

    def watch_value(self, value: str) -> None:
        """Watch the value."""
        self.cache_valid = False
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

    def watch_cache_valid(self, valid: bool) -> None:
        """Watch the cache valid value."""
        if not valid:
            self._update_cache()
            self.cache_valid = True

    def watch_app_theme(self, _: str) -> None:
        """Watch the app theme."""
        self.cache_valid = False

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

    def action_complete(self) -> None:
        """Handle complete action."""
        for cmd_name in sorted(utils.command.get_commands()):
            if cmd_name.startswith(self.value):
                self.value = cmd_name
                self.cursor_position = 1_000_000
                break

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

    def on_resize(self, event: textual.events.Resize) -> None:
        """Do stuff on resize."""
        self._render_console.width = event.size.width
        self.cache_valid = False

    def on_theme_change(self, _: textual.theme.Theme) -> None:
        """Do stuff on theme change."""
        self.cache_valid = False

    async def on_terminal_submitted(self, event: Submitted) -> None:
        """Handle terminal submit event."""
        # still a bit cursed, but it could be so much worse
        event.stop()
        # 'normal' input
        if self._input_event.is_set():
            self.history_value = -1
            if event.value:
                self._history.insert(0, event.value)
                asyncio.create_task(utils.command.parse(event.value))
            else:
                self.write_lines(utils.network.NETWORK.computer.prompt)
        # command input
        else:
            self._input_event.set()
            self._input = event.value
        # add input to last line
        self._lines[-1] += event.value

    def write_lines(self, text: str) -> None:
        """Write lines to the terminal."""
        for line_text in text.split("\n"):
            self._lines.append(line_text)
            line_text = self._replace_variables(line_text)
        self.cache_valid = False
        self.virtual_size = textual.geometry.Size(self.size.width,
                                                  len(self._lines_cache))
        self.scroll_end(animate=False, immediate=True, force=True)

    async def get_input(self, prompt: str) -> str:
        """Get input."""
        self.write_lines(prompt)
        self._input_event.clear()
        await self._input_event.wait()
        result = self._input
        return result

    def clear(self):
        """Clear the terminal."""
        self._lines.clear()
        self.cache_valid = False

    def render_line(self, y: int) -> textual.strip.Strip:
        """Render a line."""
        _, scroll_y = self.scroll_offset
        y += scroll_y
        try:
            # FIXME: figure out how to detect the input line
            # if self.cursor_visible and self.has_focus:
            #     return self._lines_cache[y]
            return self._lines_cache[y]
        except IndexError:
            return textual.strip.Strip.blank(self.size.width)
