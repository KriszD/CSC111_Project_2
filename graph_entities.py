"""Graph Classes"""
from __future__ import annotations
from collections import deque
from typing import Any, Optional


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
        - self.kind in {'movie', 'actor'}
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]
    appearences: set[str]
    cast_members: set[str]
    movie_info: tuple[int, int, float]  # (year, votes, rating)

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'actor', 'movie'}
            - self.appearences = set() or kind = 'actor'
            - self.cast_members = set() or kind = 'movie'
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()
        self.appearences = set()
        self.cast_members = set()

    def similarity_score(self, other: _Vertex) -> float:
        """Return the similarity score between this vertex and other.

        See Assignment handout for definition of similarity score.
        """
        if self.cast_members == 0 or other.cast_members == 0:
            return 0
        else:
            sim_intersection = self.cast_members.intersection(other.cast_members)
            sim_union = self.cast_members.union(other.cast_members)
            return len(sim_intersection) / len(sim_union)


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

    def add_movie_info(self, movie: str, actors: set, movie_info: tuple) -> None:
        """Adds cast members and movie info (year, votes, rating) to a movie
        Raise a ValueError if movie does not appear as a vertex in this graph."""
        if movie in self._vertices:
            self._vertices[movie].cast_members.update(actors)
            self._vertices[movie].movie_info = movie_info
        else:
            raise ValueError

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

    # def shortest_distance(self, item: str) -> tuple[dict[Any, float], dict[Any, Optional[Any]]]:
    #     """Return a dictionary mapping each vertex to the distance from the target vertex, as a dictionary
    #     mapping each vertex to their immediate parent vertex that was involved in calculating the shortest path.
    #
    #     This is an implementation of Dijkstra's shortest path algorithm.
    #     >>> g = Graph()
    #     >>> g.add_vertex('A', 'actor')
    #     >>> g.add_vertex('B', 'actor')
    #     >>> g.add_vertex('C', 'actor')
    #     >>> g.add_vertex('D', 'actor')
    #     >>> g.add_vertex('E', 'actor')
    #     >>> g.add_edge("A", "B")
    #     >>> g.add_edge("A", "C")
    #     >>> g.add_edge("B", "C")
    #     >>> g.add_edge("B", "D")
    #     >>> g.add_edge("C", "D")
    #     >>> g.add_edge("D", "E")
    #     >>> distances_of_vertices, predecessors_of_vertices = g.shortest_distance("A")
    #     >>> distances_of_vertices
    #     {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 3}
    #     >>> predecessors_of_vertices
    #     {'A': -1, 'B': 'A', 'C': 'A', 'D': 'B', 'E': 'D'}
    #     """
    #     if item not in self._vertices:
    #         raise ValueError
    #
    #     distances = {vertex: float("inf") for vertex in self._vertices}
    #     distances[item] = 0
    #
    #     predecessors: dict[Any, Optional[str]] = {vertex: None for vertex in self._vertices}
    #
    #     pq = [(0, item)]  # initialize a priority queue with the root element
    #     heapify(pq)
    #
    #     visited = set()
    #
    #     while pq:
    #         current_distance, current_vertex = heappop(pq)
    #         if current_vertex in visited:
    #             continue
    #         visited.add(current_vertex)
    #
    #         for neighbour in self._vertices[current_vertex].neighbours:
    #             possible_distance = current_distance + 1  # default weight of 1 since this is an unweighted graph
    #             if possible_distance < distances[neighbour.item]:
    #                 distances[neighbour.item] = possible_distance
    #                 predecessors[neighbour.item] = current_vertex
    #                 heappush(pq, (possible_distance, neighbour.item))
    #
    #     return distances, predecessors
    #
    # def shortest_path(self, starting_item: Any, target_item: Any) -> list[Any]:
    #     """Return a list of the item names of each vertex starting from the source item and ending with
    #     the target item that is the shortest path between the starting item and the target item.
    #
    #     This is an implementation of Dijkstra's shortest path algorithm.
    #     >>> g = Graph()
    #     >>> g.add_vertex('A', 'actor')
    #     >>> g.add_vertex('B', 'actor')
    #     >>> g.add_vertex('C', 'actor')
    #     >>> g.add_vertex('D', 'actor')
    #     >>> g.add_vertex('E', 'actor')
    #     >>> g.add_vertex('F', 'actor')
    #     >>> g.add_vertex('G', 'actor')
    #     >>> g.add_vertex('H', 'actor')
    #     >>> g.add_vertex('I', 'actor')
    #     >>> g.add_edge("A", "B")
    #     >>> g.add_edge("A", "C")
    #     >>> g.add_edge("B", "C")
    #     >>> g.add_edge("B", "D")
    #     >>> g.add_edge("C", "D")
    #     >>> g.add_edge("D", "E")
    #     >>> g.add_edge("E", "F")
    #     >>> g.add_edge("F", "G")
    #     >>> g.add_edge("G", "H")
    #     >>> g.add_edge("H", "I")
    #     >>> g.add_edge("A", "H")
    #     >>> g.add_edge("C", "G")
    #     >>> print(g.shortest_path('A', 'I'))
    #     ['A', 'H', 'I']
    #     >>> print(g.shortest_path('A', 'F'))
    #     ['A', 'C', 'G', 'F']
    #     >>> print(g.shortest_path('B', 'G'))
    #     ['B', 'C', 'G']
    #     >>> print(g.shortest_path('C', 'E'))
    #     ['C', 'D', 'E']
    #     >>> print(g.shortest_path('F', 'I'))
    #     ['F', 'G', 'H', 'I']
    #     """
    #     _, predecessors = self.shortest_distance(starting_item)
    #     path = []
    #     current_vertex = target_item
    #
    #     # return from the target vertex through the predecessors
    #     while current_vertex is not None:
    #         path.append(current_vertex)
    #         current_vertex = predecessors.get(current_vertex)
    #
    #     path.reverse()
    #
    #     if path:
    #         return path
    #     else:
    #         print("No Valid Path Found.")
    #         return []

    def get_similarity_score(self, item1: Any, item2: Any) -> float:
        """Return the similarity score between the two given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        >>> g = Graph()
        >>> for i in range(0, 6):
        ...     g.add_vertex(str(i), kind='user')
        >>> g.add_edge('0', '2')
        >>> g.add_edge('0', '3')
        >>> g.add_edge('0', '4')
        >>> g.add_edge('1', '3')
        >>> g.add_edge('1', '4')
        >>> g.add_edge('1', '5')
        >>> g.get_similarity_score('0', '1')
        0.5
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1, v2 = self._vertices[item1], self._vertices[item2]
            return v1.similarity_score(v2)
        else:
            raise ValueError

    def recommend_movies(self, movie: str, limit: Optional[int]) -> list[str]:
        """Return a list of up to <limit> recommended movies based on similarity to the given movie.

        Preconditions:
            - movie in self._vertices
            - self._vertices[movie].kind == 'movie'
            - limit >= 1
        """
        if movie not in self._vertices or self._vertices[movie].kind != 'movie':
            raise ValueError

        recommendations = {}
        for other_movie in self.get_all_vertices('movie'):
            if other_movie != movie:
                sim_score = self.get_similarity_score(movie, other_movie)
                if sim_score > 0:
                    recommendations[other_movie] = sim_score

        sorted_recommendations = sorted(recommendations, key=recommendations.get, reverse=True)
        if limit:
            return sorted_recommendations[:limit]
        else:
            return sorted_recommendations

    @staticmethod
    def sort_by_closeness(unsorted_dict: dict, value: float, threshold: float):
        """Sorting a dictionary into a list based on absolute difference"""
        filtered_items = {k: v for k, v in unsorted_dict.items() if abs(v - value) <= threshold}
        sorted_keys = sorted(filtered_items, key=lambda k: abs(filtered_items[k] - value))

        return sorted_keys

    def recommend_movies_filter(self, movie: str, limit: int, movie_filter: str, range_of_filter: float) -> list[str]:
        """Return a list of up to <limit> recommended movies based on similarity to the given movie where the movies
        have gone through a filter that filters movies based on either rating or release date.

        Preconditions:
            - movie in self._vertices
            - self._vertices[movie].kind == 'movie'
            - limit >= 1
            - filter in {'rating', 'release date'}
        """
        if movie not in self._vertices or self._vertices[movie].kind != 'movie':
            raise ValueError

        if movie_filter not in {'rating', 'release date'}:
            raise ValueError

        recommendations = self.recommend_movies(movie)
        movie_info_index = 2 if movie_filter == 'rating' else 0
        movie_value = self._vertices[movie].movie_info[movie_info_index]

        new_recommendations = {
            recommendation: self._vertices[recommendation].movie_info[movie_info_index]
            for recommendation in recommendations
        }

        sorted_recommendations = self.sort_by_closeness(new_recommendations, movie_value, range_of_filter)

        return sorted_recommendations[:limit]

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

    def shortest_distance_bfs(self, starting_item) -> dict[Any, float]:
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
                if neighbour.item not in visited:
                    visited.add(neighbour.item)
                    distances[neighbour.item] = distances[current_actor] + 1
                    queue.append(neighbour.item)

        return distances

    def average_bacon_number(self, actor: str) -> float:
        """Given an actor's name, find their average Bacon number with all other actors in the graph."""
        distances = self.shortest_distance_bfs(actor)

        total_distance = sum(dist for dist in distances.values() if dist != float("inf"))
        total_reachable = sum(1 for dist in distances.values() if dist != float("inf"))

        return total_distance / total_reachable if total_reachable > 0 else float("inf")

    def compute_average_bacon_numbers(self) -> dict:
        """Compute the average Bacon number for every actor in the graph."""
        actors = self.get_all_vertices('actor')
        average_bacon_numbers = {}

        for actor in actors:
            average_bacon_numbers[actor] = self.average_bacon_number(actor)

        return average_bacon_numbers

    def filter_by_key(self, actor1: str, actor2: str, key: str,
                      upper: int, lower: int, movies: dict) -> tuple[bool, set[str]] | None:
        """Checks if two actors have a movie connecting them that matches the given filer

        Preconditions:
        - key in {'year', 'rating'}
        """
        if actor1 in self._vertices and actor2 in self._vertices:
            v1 = self._vertices[actor1]
            v2 = self._vertices[actor2]

            if key == 'year':
                common = v1.appearences.intersection(v2.appearences)
                common_filtered = {movie for movie in common if lower <= movies[movie][1][0] <= upper}
                if common_filtered:
                    return True, common_filtered

            if key == 'rating':
                common = v1.appearences.intersection(v2.appearences)
                common_filtered = {movie for movie in common if lower <= movies[movie][1][2] <= upper}
                if common_filtered:
                    return True, common_filtered

            else:
                raise KeyError

        else:
            raise ValueError
