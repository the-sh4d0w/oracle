"""Debug commands."""

import click

import widgets.chat
import widgets.terminal


@click.command()
@click.argument("amount", type=click.INT)
def chat(amount: int) -> str:
    """Do a chat test with AMOUNT messages."""
    # cursed
    chat_widget = widgets.terminal.Terminal.TERMINAL.app.query_one(
        "#chat", widgets.chat.ChatWidget)
    for i in range(amount):
        chat_widget.write_message("zer0", f"{i} Lorem ipsum, dolor sit amet.")
    return f"sent {amount} test messages"
