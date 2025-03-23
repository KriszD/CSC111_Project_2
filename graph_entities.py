"""Graph Classes"""
from __future__ import annotations
from typing import Any, Optional
from heapq import heapify, heappop, heappush


class _Vertex:
    """A vertex in a book review graph, used to represent a user or a book.

    Each vertex item is either a user id or book title. Both are represented as strings,
    even though we've kept the type annotation as Any to be consistent with lecture.

    Instance Attributes:
        - item: The data stored in this vertex, representing a user or book.
        - kind: The type of this vertex: 'user' or 'book'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'user', 'book'}
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]
    appearences: set[str]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'actor', 'movie'}
            - self.appearences = set() or kind = 'actor'
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()
        self.appearences = set()


class Graph:
    """A graph used to represent a book review network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'book'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'user', 'book'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())

    def add_appearences(self, actor: str, movie: str) -> None:
        """Adds a movie the actor has appeared in to a set.
        Raise a ValueError if actor does not appear as a vertex in this graph."""
        if actor in self._vertices:
            self._vertices[actor].appearences.add(movie)
        else:
            raise ValueError

    def item_in_graph(self, item: str) -> bool:
        """Returns whether the given item appears as a vertex in this graph."""
        return item in self._vertices

    def shortest_distance(self, item: str) -> tuple[dict[Any, float], dict[Any, Optional[Any]]]:
        """

        :param item:
        :return:
        """
        if item not in self._vertices:
            raise ValueError

        distances = {node: float("inf") for node in self._vertices}
        distances[item] = 0

        predecessors = {node: None for node in self._vertices}

        pq = [(0, item)]  # initialize a priority queue with the root element
        heapify(pq)

        visited = set()

        while pq:
            current_distance, current_node = heappop(pq)
            if current_node in visited:
                continue
            visited.add(current_node)

            for neighbour in self._vertices[current_node].neighbours:
                possible_distance = current_distance + 1
                if possible_distance < distances[neighbour.item]:
                    distances[neighbour.item] = possible_distance
                    predecessors[neighbour.item] = current_node
                    heappush(pq, (possible_distance, neighbour.item))

        return distances, predecessors

    def shortest_path(self, starting_item: Any, target_item: Any) -> list[Any]:
        """Return a list of the item names of each node starting from the source item and ending with the target item
        that is the shortest path between the starting item and the target item.

        This is an implementation of Dijkstra's shortest path algorithm.
        >>> g = Graph()
        >>> g.add_vertex('A', 'actor')
        >>> g.add_vertex('B', 'actor')
        >>> g.add_vertex('C', 'actor')
        >>> g.add_vertex('D', 'actor')
        >>> g.add_vertex('E', 'actor')
        >>> g.add_vertex('F', 'actor')
        >>> g.add_vertex('G', 'actor')
        >>> g.add_vertex('H', 'actor')
        >>> g.add_vertex('I', 'actor')
        >>> g.add_edge("A", "B")
        >>> g.add_edge("A", "C")
        >>> g.add_edge("B", "C")
        >>> g.add_edge("B", "D")
        >>> g.add_edge("C", "D")
        >>> g.add_edge("D", "E")
        >>> g.add_edge("E", "F")
        >>> g.add_edge("F", "G")
        >>> g.add_edge("G", "H")
        >>> g.add_edge("H", "I")
        >>> g.add_edge("A", "H")
        >>> g.add_edge("C", "G")
        >>> print(g.shortest_path('A', 'I'))
        ['A', 'H', 'I']
        >>> print(g.shortest_path('A', 'F'))
        ['A', 'C', 'G', 'F']
        >>> print(g.shortest_path('B', 'G'))
        ['B', 'C', 'G']
        >>> print(g.shortest_path('C', 'E'))
        ['C', 'D', 'E']
        >>> print(g.shortest_path('F', 'I'))
        ['F', 'G', 'H', 'I']
        """
        _, predecessors = self.shortest_distance(starting_item)
        path = []
        current_node = target_item

        # return from the target node through the predecessors
        while current_node is not None:
            path.append(current_node)
            current_node = predecessors.get(current_node)

        path.reverse()

        return path
