"""A simple test website."""

import textual.app
import textual.widgets

import widgets.website


class TestWebsite(widgets.website.Website):
    """Test website."""

    def __init__(self) -> None:
        """Initialize the test website."""
        super().__init__(id_="example", title="Example",
                         keywords=["test", "example"])

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        yield self.website_header()
        yield textual.widgets.Label("[@click=app.link('slot_machine')]Try your luck![/]")
