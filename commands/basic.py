"""Basic commands."""

import click

import screens.desktop
import utils.command
import utils.computer
import widgets.chat


def logout_save() -> None:
    """Do the logout and save data."""
    utils.command.TERMINAL.app.pop_screen()
    # reinstall to reset
    utils.command.TERMINAL.app.uninstall_screen("desktop")
    utils.command.TERMINAL.app.install_screen(
        screens.desktop.DesktopScreen(), "desktop")
    # TODO: save data


def logout_confirm(answer: str) -> None:
    """Check if player actually wants to log out."""
    if answer.lower() in ("y", "yes"):
        logout_save()


@click.command()
@click.option("-y", "--yes", is_flag=True)
def logout(yes: bool) -> None:
    """Log out and save data."""
    if yes:
        logout_save()
    else:
        utils.command.ORACLE.input(
            logout_confirm, ["Do you want to log out? (y/N) "])


@click.command()
def clear() -> None:
    """Clear the terminal."""
    utils.command.TERMINAL.clear()


@click.command()
def ofetch() -> str:
    """Display system information."""
    color: str = utils.command.ORACLE.get_css_variables()["primary"]
    return rf"""
 [{color}]$$$$$$$$$[/]\    [{color}]sh4d0w@oracle[/]
 [{color}]$$[/]  ___[{color}]$$[/] |   -------------
 [{color}]$$[/] |   [{color}]$$[/] |   [{color}]OS[/]: oracleOS v1.17
 [{color}]$$[/] |   [{color}]$$[/] |   [{color}]Kernel[/]: 0.15.8.34
 [{color}]$$[/] |   [{color}]$$[/] |   [{color}]Uptime[/]: calculate this
 [{color}]$$[/] |   [{color}]$$[/] |   [{color}]Shell[/]: bosh 5.1.4
 [{color}]$$$$$$$$$[/] |   [{color}]CPU[/]: Cyclops i803 (8) @ 1.799GHz
 \_________|   [{color}]Memory[/]: 198MiB / 7812MiB
"""


@click.command()
def pwd() -> str:
    """Print working directory."""
    return utils.command.ORACLE.network.current_computer().file_system.pwd()


@click.command()
@click.option("-l", is_flag=True)
@click.option("-a", "--all", is_flag=True)
def ls(l: bool, all: bool) -> str | None:  # pylint:disable=redefined-builtin
    """List files and directories."""
    return utils.command.ORACLE.network.current_computer().file_system.ls()
    # TODO: implement better
    # if all:
    #     temp: list[utils.computer.Folder | utils.computer.File] = [
    #         utils.computer.Folder.current(), utils.computer.Folder.parent()]
    #     temp.extend(contents)
    #     contents = temp
    # if l:
    #     return "\n".join(map(str, contents))
    # return "  ".join(map(str, contents))


@click.command()
@click.argument("path", type=click.STRING, default="")
def cd(path: str) -> str | None:
    """Change directory."""
    return utils.command.ORACLE.network.current_computer().file_system.cd(path)


@click.command()
def exit() -> None:  # pylint:disable=redefined-builtin
    """Exit the current computer."""
    # TODO: implement actual computers


def login_verify(user: str, password: str) -> str:
    """Verify login."""
    if user == password == "admin":
        return "Sucessfully logged in!"
    return "Wrong username or password."


@click.command()
def login() -> None:
    """Login to the computer."""
    # FIXME: returning a string does not work
    # TODO: implement login (computer) functionality
    utils.command.ORACLE.input(login_verify, ["user: ", "pasword: "])


@click.command()
@click.argument("amount", type=click.INT)
def chat(amount: int) -> str:
    """Do a chat test."""
    # FIXME: remove later, currently for testing
    chat_widget = utils.command.ORACLE.query_one(
        "#chat", widgets.chat.ChatWidget)
    for i in range(amount):
        chat_widget.write_message("zer0", f"{i} Lorem ipsum, dolor sit amet.")
    return "sent test message"


@click.command()
def scan() -> str | None:
    """Scan for connected computers."""
    nodes = utils.command.ORACLE.network.scan()
    if len(nodes) == 0:
        return "No connected devices found."
    return "\n".join([str(node) for node in nodes])
