"""Everything used for devices."""

import enum
import re
import typing

import pydantic

import utils.file_system
import utils.network


class DeviceType(enum.StrEnum):
    """Device types."""
    TERMINAL = "terminal"   # generic PC
    CYBERDECK = "cyberdeck"  # basically smartphone
    SERVER = "server"       #
    IMPLANT = "implant"     #
    VEHICLE = "vehicle"     #


class Manufacturer(enum.StrEnum):
    """Device manufacturers."""
    OUTEL = "Outel"
    BMD = "BMD"
    CYCLOPS = "Cyclops"
    ACRON = "Acron"


class OperatingSystem(enum.StrEnum):
    """Operating systems."""
    ORACLE_OS = "oracleOS"
    CYCLOPS_OS = "CyclopsOS"


class DeviceName(enum.StrEnum):
    """Device names."""
    POWERTERM = "PowerTerm"


SYSINFO_TEXT = """
OS:         {os}
Kernel:     {kernel}
Uptime:     {uptime}
Shell:      {shell}
CPU:        {cpu}
Memory:     {memory}
"""


class NPv5Address:
    """Net Protocol v5 address. It is represented as 8 bytes seperated by dots."""
    NUM_BYTES: int = 8

    def __init__(self, address: "str | int | NPv5Address") -> None:
        """Initialize the address."""
        self.address: int = self._parse(address)

    def __repr__(self) -> str:
        """Official string representation."""
        return f"{self.__class__.__name__}({self.address})"

    def __str__(self) -> str:
        """Informal string representation."""
        return ".".join(map("{:02X}".format, list(self.address.to_bytes(self.NUM_BYTES))))

    def __hash__(self) -> int:
        """Hash of the address."""
        return hash(hex(self.address))

    def __eq__(self, other: typing.Any) -> bool:
        """Equality of the address with another object."""
        return isinstance(other, NPv5Address) and self.address == other.address

    def _parse(self, address: "str | int | NPv5Address") -> int:
        """Parse address to int from str, int, or address."""
        if isinstance(address, NPv5Address):
            return address.address
        elif isinstance(address, str):
            if match := re.fullmatch(r"\.".join(self.NUM_BYTES * ["[0-9a-fA-F]{1,2}"]), address):
                return int.from_bytes(bytes.fromhex(match.string.replace(".", "")))
        elif isinstance(address, int):
            if 0 <= address <= 2**(self.NUM_BYTES * 8) - 1:
                return address
        raise TypeError("Type not accepted.")


class Device(pydantic.BaseModel):
    """Device respresentation."""
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    # can be terminal, computer, server, brain computer, car, ...
    # do we use an actual type? (for game backend systems only)
    name: str
    """Set by user of the device."""
    net_address: NPv5Address
    """NPv5 address of the device."""
    file_system: utils.file_system.FileSystem
    """File system of the device."""
    type: DeviceType
    """Type of the device."""
    # hardware info
    manufacturer: Manufacturer
    """Name of the manufacturer."""
    device_name: str
    """Set by manufacturer."""
    username: str
    """Name of the user."""
    prompt: str
    """Terminal prompt of the device."""

    @pydantic.field_serializer("net_address")
    def _serialize_net_address(self, net_address: NPv5Address) -> int:
        """Serialize net_address (returns address as int)."""
        return net_address.address

    @pydantic.field_validator("net_address", mode="before")
    @classmethod
    def _validate_net_address(cls, value: int) -> NPv5Address:
        """Validate net_address (initialises NPv5Address with value)."""
        return NPv5Address(value)

    def sysinfo(self) -> str:
        """System info."""
        return SYSINFO_TEXT.format_map({
            "os": "oracleOS", "kernel": "lunix", "uptime": "0d 3h 17m 9s",
            "shell": "bosh", "cpu": "Cyclops i803", "memory": "???"
        })

    @classmethod
    def default(cls, name: str, net_address: NPv5Address | str | int) -> "Device":
        """Create a computer with default values except for name and IP.

        Arguments:
            - name: the name of the computer.
            - ip_address: the IP address of the computer.

        Returns:
            The computer.
        """
        return Device(name=name, net_address=NPv5Address(net_address),
                      file_system=utils.file_system.FileSystem(), type=DeviceType.TERMINAL,
                      manufacturer=Manufacturer.ACRON, device_name=DeviceName.POWERTERM,
                      username="admin", prompt="[green]{user}@{name}:{path} $[/] ")

    @classmethod
    def oracle(cls) -> "Device":
        """Create oracle."""
        return Device(name="oracle", net_address=NPv5Address(19391048),
                      file_system=utils.file_system.FileSystem(), type=DeviceType.TERMINAL,
                      manufacturer=Manufacturer.CYCLOPS, device_name=DeviceName.POWERTERM,
                      username="sh4d0w", prompt="[$primary]┌([#00FF00]{player}[/]@[#D2691E]"
                      "oracle[/])-([#FF0000]{path}[/])[/]\n[$primary]└──$[/] ")
