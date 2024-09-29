"""Everything used to simulate computers."""

import dataclasses
import enum
import ipaddress

import networkx


class FileType(enum.StrEnum):
    """All filetypes."""
    EXE = "executable"
    TXT = "text"


class Ports(enum.IntEnum):
    """Registered ports with service names."""
    # not all of these are needed or going to be used
    # TODO: DHCP?; more DNS; all the ssl versions; some old, funny ports; all of the shell services!
    # ports are not going to be accurate to year (2137)
    FTP = 20
    # 21?
    SSH = 22
    TELNET = 23
    SMTP = 25
    # network time?; ptp?
    TIME = 37
    DNS = 53
    HTTP = 80
    POP3 = 110
    IRC = 194
    IMAP = 220
    HTTPS = 443
    DOOM = 666


@dataclasses.dataclass
class File:
    """Virtual file."""
    name: str
    filetype: FileType
    content: str
    size: int = dataclasses.field(init=False)

    def __str__(self) -> str:
        """Get string representation of the file."""
        return self.name

    def __post_init__(self) -> None:
        """Initialize attributes dependent on other attributes."""
        self.size = len(self.content)

    def info(self) -> str:
        """Get info about the file.

        Returns:
            The formatted info.
        """
        return f"{self.name:15} {self.filetype:10} {self.size:>4} kB"

    @classmethod
    def text(cls, name: str, content: str) -> "File":
        """Create a text file.

        Arguments:
            - name: the name of the file.
            - content: the content of the file.

        Returns:
            The file.
        """
        # FIXME: generate random content; maybe with seed (filename)
        return File(f"{name}.txt", FileType.TXT, content)

    @classmethod
    def executable(cls, name: str) -> "File":
        """Create an executable file.

        Arguments:
            - name: the name of the file.

        Returns:
            The file.
        """
        # FIXME: generate random content
        return File(name, FileType.EXE, "01010110011101101010010111011100101")


@dataclasses.dataclass
class Folder:
    """Virtual folder."""
    name: str
    contents: list["Folder | File"]

    def __str__(self) -> str:
        """Get string representation of the folder."""
        if self.name != "." and self.name != "..":
            return f"{self.name}/"
        return self.name

    @classmethod
    def current(cls) -> "Folder":
        """Create current folder."""
        return Folder(".", [])

    @classmethod
    def parent(cls) -> "Folder":
        """Create parent folder."""
        return Folder("..", [])

    @classmethod
    def home(cls, contents: list["Folder | File"] | None = None) -> "Folder":
        """Create the home folder.

        Arguments:
            - contents: optional files and folders to add.

        Returns:
            The folder.
        """
        if contents is None:
            return Folder("home", [])
        return Folder("home", contents)

    @classmethod
    def bin(cls, contents: list["Folder | File"] | None = None) -> "Folder":
        """Create the bin folder.

        Arguments:
            - contents: optional files and folders to add.

        Returns:
            The folder.
        """
        if contents is None:
            return Folder("bin", [File.executable("test")])
        return Folder("bin", contents)

    @classmethod
    def default_root(cls) -> "Folder":
        """Create the default folder structure."""
        # FIXME: __str__ produces // with root
        return Folder("/", [Folder.home(), Folder.bin()])


@dataclasses.dataclass
class Computer:
    """Virtual computer."""
    name: str
    ip_address: ipaddress.IPv4Address
    root_folder: Folder
    user: str
    password: str

    def __str__(self) -> str:
        """Get string representation of the computer."""
        return self.name

    def __hash__(self) -> int:
        """Get hash of computer (ip_address).

        Return:
            The hashed value.
        """
        return hash(self.ip_address)

    @classmethod
    def default(cls, name: str, ip_address: ipaddress.IPv4Address | str | int) -> "Computer":
        """Create a computer with default values except for name and IP.

        Arguments:
            - name: the name of the computer.
            - ip_address: the IP address of the computer.

        Returns:
            The computer.
        """
        return Computer(name, ipaddress.IPv4Address(ip_address), Folder.default_root(),
                        "admin", "admin")


class Network:
    """Virtual network."""
    # functions mimic terminal commands

    def __init__(self) -> None:
        """Initialize the network."""
        # oracle as default home
        oracle = Computer.default("oracle", 19391048)
        self._graph: networkx.Graph = networkx.Graph()
        self._nodes: dict[ipaddress.IPv4Address, Computer] = {}
        self._home: ipaddress.IPv4Address = oracle.ip_address
        self._current: ipaddress.IPv4Address = self._home
        self.add_node(oracle)

    @property
    def current(self) -> ipaddress.IPv4Address:
        """The node currently connected."""
        return self._current

    @current.setter
    def current(self, new_current: ipaddress.IPv4Address | str | int) -> None:
        self._current = ipaddress.IPv4Address(new_current)

    def add_node(self, node: Computer) -> None:
        """Add a node to the network.

        Arguments:
            - node: the node to add.
        """
        self._graph.add_node(node.ip_address)
        self._nodes[node.ip_address] = node

    def add_connection(self, first_node: ipaddress.IPv4Address | str | int,
                       second_node: ipaddress.IPv4Address | str | int) -> None:
        """Add a connection between two nodes (two-directional).

        Arguments:
            - first_node: the IP of the first node of the connection.
            - second_node: the IP of the second node of the connection.
        """
        first_node = ipaddress.IPv4Address(first_node)
        second_node = ipaddress.IPv4Address(second_node)
        self._graph.add_edge(first_node, second_node)

    def scan(self) -> list[ipaddress.IPv4Address]:
        """Get all nodes connected to the current node.

        Returns:
            All connected nodes.
        """
        return list(self._graph.neighbors(self._current))

    def connect(self, ip_address: ipaddress.IPv4Address | str | int) -> bool:
        """Connect to a node.

        Arguments:
            - ip_address: IP of the node to connect to.

        Returns:
            True if successful, False otherwise.
        """
        ip_address = ipaddress.IPv4Address(ip_address)
        if ip_address in self._nodes:
            self._current = ip_address
            return True
        return False

    def disconnect(self) -> None:
        """Disconnect from a node."""
        self._current = self._home

# TODO: computer needs to be able to stand on its own
# navigating through the network and computers

# TODO: load and save network from/to JSON -> pydantic?

# connected means some sort of direct access is possible (e.g. SSH, Telnet, ...)
# -> on the system!


if __name__ == "__main__":
    network = Network()
    network.add_node(Computer.default("Batcomputer", 3789367))
    network.add_node(Computer.default("Gugle (DNS)", "8.8.8.8"))
    network.add_node(Computer.default("Gugle Search", "11.57.69.102"))
    network.add_connection("8.8.8.8", "11.57.69.102")
    print(network.current)
    network.connect("8.8.8.8")
    print(network.current)
    print(network.scan())
    network.disconnect()
    print(network.current)
