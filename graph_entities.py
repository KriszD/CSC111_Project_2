"""Graph Classes"""
from __future__ import annotations
from collections import deque
from typing import Any

import python_ta


class _Vertex:
    """A vertex in a book review graph, used to represent a user or a book.

    Each vertex item is either an actor or movie.

    Instance Attributes:
        - item: The data stored in this vertex, representing an actor or movie.
        - kind: The type of this vertex: 'actor' or 'movie'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'movie', 'actor'}
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]
    appearences: set[str]
    sim_score: float
    movie_info: tuple[int, int, float]  # (year, votes, rating)

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
        self.sim_score = 0


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

    def get_vertices(self) -> dict:
        """Return the dictionary of vertices in the graph."""
        return self._vertices

    def add_appearences(self, actor: str, movie: str) -> None:
        """Adds a movie the actor has appeared in to a set.
        Raise a ValueError if actor does not appear as a vertex in this graph."""
        if actor in self._vertices:
            self._vertices[actor].appearences.add(movie)
        else:
            raise ValueError

    # def add_movie_info(self, movie: str, actors: set, movie_info: tuple) -> None:
    #     """Adds cast members and movie info (year, votes, rating) to a movie
    #     Raise a ValueError if movie does not appear as a vertex in this graph."""
    #     if movie in self._vertices:
    #         self._vertices[movie].cast_members.update(actors)
    #         self._vertices[movie].movie_info = movie_info
    #     else:
    #         raise ValueError

    def add_sim_score(self, movie: str, sim_score: dict | float) -> None:
        """Adds a movie's similarity score."""
        if isinstance(sim_score, dict):
            sim_score = sim_score[movie]
        self._vertices[movie].sim_score = sim_score

    def item_in_graph(self, item: str) -> bool:
        """Returns whether the given item appears as a vertex in this graph."""
        return item in self._vertices

    def get_common_movies(self, item1: str, item2: str) -> set:
        """Returns the movie(s) that are in common between two actors"""
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            return v1.appearences.intersection(v2.appearences)
        else:
            raise ValueError

    def get_appearences(self, actor: str) -> set:
        """Returns a set of movies an actor has appeared in"""
        return self._vertices[actor].appearences

    ####################################################################################################################
    # BFS (Breadth First Search)
    ####################################################################################################################

    def shortest_path_bfs(self, starting_item: str, target_item: str) -> str | list[Any]:
        """Find the shortest path between two actors using BFS."""
        if starting_item not in self._vertices or target_item not in self._vertices:
            raise ValueError

        queue = deque([(starting_item, [starting_item])])
        visited = {starting_item}

        while queue:
            current_actor, path = queue.popleft()

            if current_actor == target_item:
                return path

            for neighbour in self._vertices[current_actor].neighbours:
                if neighbour.item not in visited:
                    visited.add(neighbour.item)
                    queue.append((neighbour.item, path + [neighbour.item]))

        return []

    def shortest_path_bfs_filtered(self, starting_item: str, target_item: str, key: str,
                                   upper: float, lower: float, movies: dict) -> str | list[Any]:
        """Find the shortest path between two actors using BFS where actors can only be included in the path
        if they match the filtering requirements."""
        if starting_item not in self._vertices or target_item not in self._vertices:
            raise ValueError

        queue = deque([(starting_item, [starting_item])])
        visited = {starting_item}

        while queue:
            current_actor, path = queue.popleft()

            if current_actor == target_item:
                return path

            for neighbour in self._vertices[current_actor].neighbours:
                if neighbour.item not in visited:
                    is_valid, _ = self.filter_by_key(current_actor, neighbour.item, key, upper, lower, movies)
                    if is_valid:
                        visited.add(neighbour.item)
                        queue.append((neighbour.item, path + [neighbour.item]))

        return []

    def shortest_distance_bfs(self, starting_item: str) -> dict[Any, float]:
        """Compute the shortest distance from a given actor to all other actors using BFS."""
        if starting_item not in self._vertices:
            raise ValueError

        distances = {actor: float("inf") for actor in self._vertices}
        distances[starting_item] = 0

        queue = deque([starting_item])
        visited = {starting_item}

        while queue:
            current_actor = queue.popleft()

            for neighbour in self._vertices[current_actor].neighbours:
                if neighbour.item != starting_item and neighbour.item not in visited:
                    visited.add(neighbour.item)
                    distances[neighbour.item] = distances[current_actor] + 1
                    queue.append(neighbour.item)

        # Remove the starting actor
        return {actor: dist for actor, dist in distances.items() if actor != starting_item}

    def filter_by_key(self, actor1: str, actor2: str, key: str,
                      lower: float, upper: float, movies: dict) -> tuple[bool, set[str]] | None:
        """Checks if two actors have a movie connecting them that matches the given filter.

        Preconditions:
        - key in {'year', 'rating'}
        """
        if actor1 in self._vertices and actor2 in self._vertices:
            v1 = self._vertices[actor1]
            v2 = self._vertices[actor2]

            if key == 'year':
                common = v1.appearences.intersection(v2.appearences)
                common_filtered = {movie for movie in common if lower <= float(movies[movie][1][0]) <= upper}
                if common_filtered:
                    return True, common_filtered

            if key == 'rating':
                common = v1.appearences.intersection(v2.appearences)
                common_filtered = {movie for movie in common if lower <= float(movies[movie][1][2]) <= upper}
                if common_filtered:
                    return True, common_filtered

            else:
                raise KeyError

        else:
            raise ValueError

        return False, set()


if __name__ == '__main__':
    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
