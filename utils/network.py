"""Everything used for networks."""

import networkx

import utils.device
import utils.file_system


class DNS:
    """Domain Name System."""

    def __init__(self) -> None:
        """Initialise the DNS."""
        self._dns: dict[str, utils.device.NPv5Address] = {}


class Network:
    """Virtual network."""
    # oracle has a network, so everything should be directly accessible here

    def __init__(self) -> None:
        """Initialize the network."""
        # oracle as default home -> FIXME: maybe load from file
        oracle = utils.device.Device.oracle()
        self._graph: networkx.Graph = networkx.Graph()
        self._nodes: dict[utils.device.NPv5Address, utils.device.Device] = {}
        self._home: utils.device.NPv5Address = oracle.net_address
        self._current: utils.device.NPv5Address = self._home
        self.add_node(oracle)
        # FIXME: remove later; for test purposes only
        zer0 = utils.device.Device.default("zer0's server", 12345)
        self.add_node(zer0)
        self.add_connection(oracle.net_address, zer0.net_address)

    @property
    def computer(self) -> utils.device.Device:
        """Get the current computer."""
        return self._nodes[self._current]

    @property
    def file_system(self) -> utils.file_system.FileSystem:
        """Get the current computer's filesystem."""
        return self.computer.file_system

    def add_node(self, node: utils.device.Device) -> None:
        """Add a node to the network.

        Arguments:
            - node: the node to add.
        """
        self._graph.add_node(node.net_address)
        self._nodes[node.net_address] = node

    def add_connection(self, first_node: utils.device.NPv5Address | str | int,
                       second_node: utils.device.NPv5Address | str | int) -> None:
        """Add a connection between two nodes (two-directional).

        Arguments:
            - first_node: the IP of the first node of the connection.
            - second_node: the IP of the second node of the connection.
        """
        first_node = utils.device.NPv5Address(first_node)
        second_node = utils.device.NPv5Address(second_node)
        self._graph.add_edge(first_node, second_node)

    def scan(self) -> list[utils.device.NPv5Address]:
        """Get all nodes connected to the current node.

        Returns:
            All connected nodes.
        """
        return list(self._graph.neighbors(self._current))

    def connect(self, net_address: utils.device.NPv5Address | str | int) -> bool:
        """Connect to a node.

        Arguments:
            - ip_address: IP of the node to connect to.

        Returns:
            True if successful, False otherwise.
        """
        net_address = utils.device.NPv5Address(net_address)
        if net_address in self._nodes:
            self._current = net_address
            return True
        return False

    def disconnect(self) -> None:
        """Disconnect from a node."""
        self._current = self._home

    @classmethod
    def _load(cls) -> "Network":
        """Load network from (save?) file."""
        return Network()

    @classmethod
    def _store(cls) -> None:
        """Store network in (save?) file."""


# TODO: load?; technically everything should go into the save file, but the network is not \
# player dependent
NETWORK = Network()
