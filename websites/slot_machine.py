"""Slot machine website."""

import random

import textual.app
import textual.containers
import textual.widget
import textual.widgets

import widgets.website

# TODO: money?
# -> win every 7th maybe; big wins less often -> rig the game


class SlotMachineWebsite(widgets.website.Website):
    """Slot machine website."""

    symbols: list[str] = ["💍", "🍒", "💎", "🔔", "👑", "🍀", "🍉"]

    def __init__(self) -> None:
        """Initialize the slot machine website."""
        super().__init__(id_="slot_machine", title="Mega Jackpot",
                         keywords=["jackpot", "mega", "gambling", "luck", "slot", "machine"])

    def compose(self) -> textual.app.ComposeResult:
        """Compose the ui."""
        yield self.website_header()
        with textual.containers.Vertical(id="slot_vertical"):
            with textual.containers.Container(id="slot_title_container"):
                yield textual.widgets.Label("MEGA JACKPOT", id="slot_title")
            with textual.containers.Horizontal(id="slot_horizontal"):
                yield textual.widgets.Label(self.symbols[0], id="slot1", classes="slot")
                yield textual.widgets.Label(self.symbols[1], id="slot2", classes="slot")
                yield textual.widgets.Label(self.symbols[2], id="slot3", classes="slot")
            with textual.containers.Container(id="slot_spin_container"):
                yield textual.widgets.Button("SPIN", id="slot_spin_button")

    @textual.on(textual.widgets.Button.Pressed, "#slot_spin_button")
    def pressed_slot_spin_button(self, event: textual.widgets.Button.Pressed) -> None:
        """Handle button pressed event for slot_spin_button."""
        event.stop()
        slot1 = self.query_one("#slot1", textual.widgets.Label)
        slot2 = self.query_one("#slot2", textual.widgets.Label)
        slot3 = self.query_one("#slot3", textual.widgets.Label)
        slot1.update(random.choice(self.symbols))
        slot2.update(random.choice(self.symbols))
        slot3.update(random.choice(self.symbols))
        # TODO: pop up
