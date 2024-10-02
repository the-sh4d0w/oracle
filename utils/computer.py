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
    parent: "Directory | None"
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
        return File(f"{name}.txt", None, FileType.TXT, content)

    @classmethod
    def executable(cls, name: str) -> "File":
        """Create an executable file.

        Arguments:
            - name: the name of the file.

        Returns:
            The file.
        """
        # FIXME: generate random content
        return File(name, None, FileType.EXE, "01010110011101101010010111011100101")


@dataclasses.dataclass
class Directory:
    """Virtual directory."""
    name: str
    parent: "Directory | None"
    children: list["Directory"]
    files: list["File"]

    def __str__(self) -> str:
        """Get string representation."""
        return f"{self.name}/"

    def add_child(self, child: "Directory | File") -> None:
        """Add a child to the directory."""
        child.parent = self
        if isinstance(child, Directory):
            self.children.append(child)
        else:
            self.files.append(child)

    @classmethod
    def home(cls) -> "Directory":
        """Create home directory."""
        return cls("home", None, [], [])

    @classmethod
    def bin(cls) -> "Directory":
        """Create bin directory."""
        return cls("bin", None, [], [])

    @classmethod
    def root(cls) -> "Directory":
        """Create root directory."""
        root = cls("", None, [], [])
        root.add_child(cls.home())
        bin_ = cls.bin()
        bin_.add_child(File.executable("test"))
        root.add_child(bin_)
        return root


class FileSystem:
    """Virtual file system."""

    class NoSuchDirectoryException(Exception):
        """No such directory exception."""

    def __init__(self, root: Directory = Directory.root()) -> None:
        """Initialize the file system."""
        self.root: Directory = root
        self.working_directory: Directory = self.root

    def _walk(self, start: Directory, path: list[str]) -> Directory:
        """Walk through a path."""
        if len(path) == 0:
            return start
        step = path.pop(0)
        # same directory
        if step == ".":
            return self._walk(start, path)
        # parent directory
        if step == "..":
            if start.parent is not None:
                return self._walk(start.parent, path)
            # start is root
            return self._walk(start, path)
        # child directory
        for child in start.children:
            if child.name == step:
                return self._walk(child, path)
        # raise error if child doesn't exist
        raise self.NoSuchDirectoryException()

    def pwd(self) -> str:
        """Get current working directory."""
        path = []
        node: Directory = self.working_directory
        while True:
            path.insert(0, node)
            if node.parent is not None:
                node = node.parent
            else:
                break
        return "".join(map(str, path))

    def ls(self) -> str | None:
        """List content of directory."""
        if len(self.working_directory.children) == 0 and len(self.working_directory.files) == 0:
            return None
        return " ".join(map(str, self.working_directory.children)) + " " \
            + " ".join(map(str, self.working_directory.files))

    def cd(self, path: str) -> str | None:
        """Change directory."""
        path_parts = path.removesuffix("/").split("/")
        try:
            # absolute path
            if path_parts[0] == "":
                self.working_directory = self._walk(self.root, path_parts[1:])
            # relative path
            else:
                self.working_directory = self._walk(
                    self.working_directory, path_parts)
        except FileSystem.NoSuchDirectoryException:
            return "no such directory"


@dataclasses.dataclass
class Computer:
    """Virtual computer."""
    name: str
    ip_address: ipaddress.IPv4Address
    file_system: FileSystem
    user: str
    password: str | None
    prompt: str
    big_prompt: str | None

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
        return Computer(name, ipaddress.IPv4Address(ip_address), FileSystem(),
                        "admin", "admin", "{user}@{name}:{path} ", None)

    @classmethod
    def oracle(cls) -> "Computer":
        """Create oracle."""
        return Computer("oracle", ipaddress.IPv4Address(19391048), FileSystem(),
                        "sh4d0w", None, "[{primary}]└──$[/] ", "[{primary}]┌([#00FF00]"
                        "{player}[/]@[#D2691E]oracle[/])-([#FF0000]{path}[/])[/]")


class Network:
    """Virtual network."""
    # functions mimic terminal commands

    def __init__(self) -> None:
        """Initialize the network."""
        # oracle as default home -> why????
        # FIXME: this; maybe access computer directly or atleast make it possible to do so
        oracle = Computer.oracle()
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

    def current_computer(self) -> Computer:
        """Get the current computer.

        Returns:
            The computer.
        """
        return self._nodes[self.current]

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
