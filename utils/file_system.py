"""Everything used for file systems."""

import dataclasses
import enum
import random


class FileType(enum.StrEnum):
    """All filetypes."""
    EXE = "executable"
    TXT = "text"


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
        match self.filetype:
            case FileType.EXE:
                return self.name
            case FileType.TXT:
                return f"{self.name}.txt"

    def __post_init__(self) -> None:
        """Initialize attributes dependent on other attributes."""
        self.size = len(self.content)

    def info(self) -> str:
        """Get info about the file.

        Returns:
            The formatted info.
        """
        return f"{self.filetype:10} {self.size:>4} kB {self}"

    @classmethod
    def text(cls, name: str, content: str) -> "File":
        """Create a text file.

        Arguments:
            - name: the name of the file.
            - content: the content of the file.

        Returns:
            The file.
        """
        return File(name, None, FileType.TXT, content)

    @classmethod
    def executable(cls, name: str) -> "File":
        """Create an executable file.

        Arguments:
            - name: the name of the file.

        Returns:
            The file.
        """
        size: int = len(name) * random.randint(0, 7)
        content: str = "".join([str(random.randint(0, 1))
                               for _ in range(size)])
        return File(name, None, FileType.EXE, content)


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

    def info(self) -> str:
        """Get info about the file.

        Returns:
            The formatted info.
        """
        return f"directory  ({len(self.children):>2}|{len(self.files):>2}) " \
            f"[#0000FF]{self.name}[/]"

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
        root.add_child(cls.bin())
        home = cls.home()
        home.add_child(File.executable("foo"))
        home.add_child(File.text("bar", "Lorem ipsum, dolor sit amet."))
        home.add_child(Directory("test", None, [], []))
        root.add_child(home)
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
        raise self.NoSuchDirectoryException(step)

    def pwd(self) -> str:
        """Get current working directory."""
        # step all the way back to root
        path: list[Directory] = []
        node: Directory = self.working_directory
        while True:
            path.insert(0, node)
            if node.parent is not None:
                node = node.parent
            else:
                break
        # remove / if not root
        wd: str = "".join(map(str, path))
        if wd != "/":
            wd = wd.removesuffix("/")
        return wd

    def ls(self, list_: bool = False, all_: bool = False) \
            -> tuple[list[str] | None, list[str] | None]:
        """List content of directory.

        Arguments:
            - list_: uses list format with info if True.
            - all: adds . and .. to output if True.

        Returns:
            A list of directories and a list of files. Can be None if empty.
        """
        # yeah, this has become cursed again
        directories: list[tuple[str, str]] = []
        files: list[str] = []
        # add . and .. if all
        if all_:
            # info if list
            if list_:
                current: Directory = self.working_directory
                parent: Directory = self.working_directory.parent \
                    if self.working_directory.parent else self.working_directory
                directories += [
                    (".", f"directory  ({len(current.children):>2}|{len(current.files):>2}) "
                     "[#0000FF].[/]"),
                    ("..", f"directory  ({len(parent.children):>2}|{len(parent.files):>2}) "
                     "[#0000FF]..[/]")
                ]
            else:
                directories += [(".", "."), ("..", "..")]
        # info if list
        if list_:
            directories += map(lambda directory: (str(directory), directory.info()),
                               self.working_directory.children)
            files += map(lambda file: file.info(),
                         self.working_directory.files)
        # name if not list
        else:
            directories += map(lambda child: (str(child), f"[#0000FF]{child.name}[/]"),
                               self.working_directory.children)
            files += map(str, self.working_directory.files)
        return list(map(lambda t: t[1], sorted(directories, key=lambda t: t[0]))) \
            if len(directories) > 0 else None, sorted(files) if len(files) > 0 else None

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
            return None
        except FileSystem.NoSuchDirectoryException as excp:
            return f"No such directory '{excp}'."
