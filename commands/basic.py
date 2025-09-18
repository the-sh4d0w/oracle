"""Basic commands."""

import click

import utils.command
import utils.device
import utils.network
import utils.values
import widgets.terminal


@click.command()
@click.argument("command", type=click.STRING, default="")
def help(command: str) -> None:  # pylint:disable=redefined-builtin
    """Show help for COMMAND or list all commands without COMMAND parameter."""
    if command == "":
        result: list[str] = []
        for name, cmd in sorted(utils.command.COMMANDS.items()):
            result.append(f"[$primary]{name:10}[/] {cmd.__doc__}")
        utils.command.print("\n".join(result))
    elif command in utils.command.COMMANDS:
        utils.command.print(str(utils.command.COMMANDS[command].get_help(
            click.Context(utils.command.COMMANDS[command]))))
    else:
        utils.command.print(f"No help exists for '{command}'.")


def logout_save() -> None:
    """Do the logout and save data."""
    widgets.terminal.Terminal.TERMINAL.app.pop_screen()
    # TODO: save data


@click.command()
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
async def logout(yes: bool) -> None:
    """Log out and save data."""
    if yes:
        logout_save()
    else:
        answer = await utils.command.input("Do you want to log out? (y/N) ")
        if answer.lower() in ("y", "yes"):
            logout_save()


@click.command()
def clear() -> None:
    """Clear the terminal."""
    utils.command.clear()


@click.command()
def ofetch() -> None:
    """Display system information."""
    # FIXME: match information to boot screen
    utils.command.print(r"""
 [$primary]$$$$$$$$$[/]\    [$primary]{user}@{name}[/]
 [$primary]$$[/]  ___[$primary]$$[/] |   -------------
 [$primary]$$[/] |   [$primary]$$[/] |   [$primary]OS[/]: oracleOS v1.17
 [$primary]$$[/] |   [$primary]$$[/] |   [$primary]Kernel[/]: v0.15.8.34
 [$primary]$$[/] |   [$primary]$$[/] |   [$primary]Uptime[/]: calculate this
 [$primary]$$[/] |   [$primary]$$[/] |   [$primary]Shell[/]: bosh 5.1.4
 [$primary]$$$$$$$$$[/] |   [$primary]CPU[/]: Cyclops i803 (8) @ 1.799GHz
 \_________|   [$primary]Memory[/]: 198MiB / 7812MiB
""".format_map(utils.values.VALUES.as_dict()))


@click.command()
def pwd() -> None:
    """Print working directory."""
    utils.command.print(utils.network.NETWORK.file_system.pwd())


@click.command()
@click.option("-l", is_flag=True, help="Format as list.")
@click.option("-a", "--all", is_flag=True, help="Show dot-prefixed files and directories.")
def ls(l: bool, all: bool) -> None:  # pylint:disable=redefined-builtin
    """List files and directories."""
    # TODO: add option to list specific folder
    # feels a bit cursed
    directories: list[str] | None
    files: list[str] | None
    header: str = "[bold italic]type       size    name[/]\n"
    output: str = ""
    directories, files = utils.network.NETWORK.file_system.ls(l, all)
    if directories is not None:
        output += ("\n" if l else " ").join(directories)
    if files is not None:
        if output != "":
            output += ("\n" if l else " ")
        output += ("\n" if l else " ").join(files)
    if l and output != "":
        output = header + output
    if output:
        utils.command.print(output)


@click.command()
@click.argument("path", type=click.STRING, default="")
def cd(path: str) -> None:
    """Change directory to PATH."""
    if output := utils.network.NETWORK.file_system.cd(path):
        utils.command.print(output)


@click.command()
async def login() -> None:
    """Login to the computer."""
    # TODO: implement login (computer) functionality
    user = await utils.command.input("user: ")
    password = await utils.command.input("passsword: ")
    if user == password == "admin":
        utils.command.print("Succcessfully logged in!")
    else:
        utils.command.print("Wrong username or password.")


@click.command()
def scan() -> None:
    """Scan for connected computers."""
    nodes = utils.network.NETWORK.scan()
    if len(nodes) == 0:
        utils.command.print("No connected devices found.")
    else:
        utils.command.print("\n".join([str(node) for node in nodes]))


@click.command()
@click.argument("ip_address", type=click.STRING)
def connect(ip_address: str) -> None:
    """Connect to the computer with the IP_ADDRESS."""
    if not utils.network.NETWORK.connect(utils.device.NPv5Address(ip_address)):
        utils.command.print("Could not connect.")


@click.command()
def exit() -> None:  # pylint:disable=redefined-builtin
    """Exit the current computer."""
    utils.network.NETWORK.disconnect()
