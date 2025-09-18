"""Debug commands."""

import asyncio

import click

import utils.command
import widgets.chat
import widgets.terminal


@click.command()
@click.argument("amount", type=click.INT)
def chat(amount: int) -> None:
    """Do a chat test with AMOUNT messages."""
    # cursed
    chat_widget = widgets.terminal.Terminal.TERMINAL.app.screen.query_one(
        "#chat", widgets.chat.ChatWidget)
    for i in range(amount):
        chat_widget.write_message("zer0", f"{i} Lorem ipsum, dolor sit amet.")
    utils.command.print(f"sent {amount} test messages")


@click.command(name="quit")
def quit_() -> None:
    """Quit the game."""
    widgets.terminal.Terminal.TERMINAL.app.exit()


@click.command()
def hack() -> None:
    """Hacking minigame test."""
    utils.command.print(
        "\n".join(["0 1 2 [@click=app.link('slot_machine')]3[/] 4 5 6 7 8 9"] * 7))


@click.command()
async def echo() -> None:
    """Echo input."""
    result = await utils.command.input("echo> ")
    utils.command.print(result)


@click.command()
async def wait() -> None:
    """Wait."""
    await asyncio.sleep(7)
