"""Debug commands."""

import click

import utils.command
import widgets.chat


@click.command()
@click.argument("amount", type=click.INT)
def chat(amount: int) -> str:
    """Do a chat test with AMOUNT messages."""
    chat_widget = utils.command.ORACLE.query_one(
        "#chat", widgets.chat.ChatWidget)
    for i in range(amount):
        chat_widget.write_message("zer0", f"{i} Lorem ipsum, dolor sit amet.")
    return f"sent {amount} test messages"
