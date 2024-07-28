"""Everything used to simulate computers."""

import dataclasses
import enum


class FileType(enum.StrEnum):
    """All filetypes."""
    EXE = "executable"
    TXT = "text"


@dataclasses.dataclass
class File:
    """Virtual file."""
    name: str
    filetype: FileType
    content: str
    size: int = dataclasses.field(init=False)

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
            return Folder("home", [File.executable("test")])
        return Folder("home", contents)

    @classmethod
    def default_root(cls) -> "Folder":
        """Create the default folder structure."""
        return Folder("/", [Folder.home(), Folder.bin()])


@dataclasses.dataclass
class Computer:
    """Virtual computer."""
    name: str
    ip_address: str
    root_folder: Folder
    user: str
    password: str

    def __str__(self) -> str:
        """Get string representation of the computer.

        Returns:
            The name of the computer.
        """
        return self.name

    @classmethod
    def default(cls, name: str, ip_address) -> "Computer":
        """Create a computer with default values except for name and IP.

        Arguments:
            - name: the name of the computer.
            - ip_address: the IP address of the computer.

        Returns:
            The computer.
        """
        return Computer(name, ip_address, Folder.default_root(), "admin", "admin")


class Network:
    """Virtual network."""

    def __init__(self) -> None:
        """Initialize the network."""
        self.nodes: set[Computer] = set()
        self.pairs: set[tuple[Computer, Computer]] = set()

    def get_connected_nodes(self, node: Computer) -> set[Computer]:
        """Get all connected nodes."""
        connected = set()
        for pair in self.pairs:
            if pair[0] == node:
                connected.add(pair[1])
        return connected

    def add_node(self, node: Computer, nodes: set[Computer] | None = None) -> None:
        """Add a node to the network."""
        self.nodes.add(node)
        if nodes is None:
            nodes = set()
        for connected in nodes:
            self.pairs.add((node, connected))
