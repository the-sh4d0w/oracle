"""Basic commands."""

import ipaddress

import click

import utils.command
import utils.computer
import utils.values
import widgets.terminal


@click.command(add_help_option=False)
@click.argument("command", type=click.STRING, default="")
def help(command: str) -> str:  # pylint:disable=redefined-builtin
    """Show help for COMMAND or list all commands without COMMAND parameter."""
    if command == "":
        return "\n".join([f"{name:10} {cmd.__doc__}"
                          for name, cmd in sorted(utils.command.COMMANDS.items())])
    if command in utils.command.COMMANDS:
        return str(utils.command.COMMANDS[command].get_help(
            click.Context(utils.command.COMMANDS[command])))
    return f"No help exists for '{command}'."


def logout_save() -> None:
    """Do the logout and save data."""
    widgets.terminal.Terminal.TERMINAL.app.pop_screen()
    # TODO: save data


def logout_confirm(answer: str) -> None:
    """Check if player actually wants to log out."""
    if answer.lower() in ("y", "yes"):
        logout_save()


@click.command()
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
def logout(yes: bool) -> None:
    """Log out and save data."""
    if yes:
        logout_save()
    else:
        widgets.terminal.Terminal.TERMINAL.input(
            logout_confirm, "Do you want to log out? (y/N) ")


@click.command()
def clear() -> None:
    """Clear the terminal."""
    widgets.terminal.Terminal.TERMINAL.clear()


@click.command()
def ofetch() -> str:
    """Display system information."""
    # FIXME: match information to boot screen
    return r"""
 [{primary}]$$$$$$$$$[/]\    [{primary}]{user}@{name}[/]
 [{primary}]$$[/]  ___[{primary}]$$[/] |   -------------
 [{primary}]$$[/] |   [{primary}]$$[/] |   [{primary}]OS[/]: oracleOS v1.17
 [{primary}]$$[/] |   [{primary}]$$[/] |   [{primary}]Kernel[/]: v0.15.8.34
 [{primary}]$$[/] |   [{primary}]$$[/] |   [{primary}]Uptime[/]: calculate this
 [{primary}]$$[/] |   [{primary}]$$[/] |   [{primary}]Shell[/]: bosh 5.1.4
 [{primary}]$$$$$$$$$[/] |   [{primary}]CPU[/]: Cyclops i803 (8) @ 1.799GHz
 \_________|   [{primary}]Memory[/]: 198MiB / 7812MiB
""".format_map(utils.values.VALUES.as_dict())


@click.command()
def pwd() -> str:
    """Print working directory."""
    return utils.computer.NETWORK.file_system.pwd()


@click.command()
@click.option("-l", is_flag=True, help="Format as list.")
@click.option("-a", "--all", is_flag=True, help="Show dot-prefixed files and directories.")
def ls(l: bool, all: bool) -> str | None:  # pylint:disable=redefined-builtin
    """List files and directories."""
    # TODO: add option to list specific folder
    # feels a bit cursed
    directories: list[str] | None
    files: list[str] | None
    header: str = "[bold italic]type       size    name[/]\n"
    output: str = ""
    directories, files = utils.computer.NETWORK.file_system.ls(l, all)
    if directories is not None:
        output += ("\n" if l else " ").join(directories)
    if files is not None:
        if output != "":
            output += ("\n" if l else " ")
        output += ("\n" if l else " ").join(files)
    if l and output != "":
        output = header + output
    return output if output != "" else None


@click.command()
@click.argument("path", type=click.STRING, default="")
def cd(path: str) -> str | None:
    """Change directory to PATH."""
    return utils.computer.NETWORK.file_system.cd(path)


def login_verify(user: str, password: str) -> str:
    """Verify login."""
    if user == password == "admin":
        return "Sucessfully logged in!"
    return "Wrong username or password."


@click.command()
def login() -> None:
    """Login to the computer."""
    # TODO: implement login (computer) functionality
    widgets.terminal.Terminal.TERMINAL.input(
        login_verify, "user: ", "pasword: ")


@click.command()
def scan() -> str | None:
    """Scan for connected computers."""
    nodes = utils.computer.NETWORK.scan()
    if len(nodes) == 0:
        return "No connected devices found."
    return "\n".join([str(node) for node in nodes])


@click.command()
@click.argument("ip_address", type=click.STRING)
def connect(ip_address: str) -> str | None:
    """Connect to the computer with the IP_ADDRESS."""
    if not utils.computer.NETWORK.connect(ipaddress.IPv4Address(ip_address)):
        return "Could not connect."
    return None


@click.command()
def exit() -> None:  # pylint:disable=redefined-builtin
    """Exit the current computer."""
    utils.computer.NETWORK.disconnect()
