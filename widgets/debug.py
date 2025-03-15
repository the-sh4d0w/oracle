"""Debug widget."""

import textual.app
import textual.widget
import textual.widgets

import main


class DebugWidget(textual.widget.Widget):
    """Debug widget."""

    def __init__(self, id_: str | None = None) -> None:
        """Initialize the debug widget."""
        super().__init__(id=id_)

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        yield textual.widgets.Label(f"Game version: {'.'.join(map(str, main.__VERSION__))}")
        yield textual.widgets.Placeholder()
