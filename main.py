"""Running the program"""
from graph_entities import Graph
import graph_create


def bacon_path(graph: Graph, actor1: str, actor2: str) -> tuple[list, list]:
    """Given the name of two actors, find the path between them, return two lists, one with movies and one without"""
    actors = graph.get_all_vertices('actor')
    if actor1 not in actors or actor2 not in actors:
        print("At least one of those actors is not in this graph.")
        raise ValueError
    path = graph.shortest_path(actor1, actor2)
    path_with_movies = []

    for i in range(len(path) - 1):
        path_with_movies.append(path[i])  # add actor
        movies = graph.get_common_movies(path[i], path[i + 1])  # get intersecting movies
        path_with_movies.append(movies)  # add movie(s)

    path_with_movies.append(path[-1])  # add back the final actor

    return path, path_with_movies


def print_bacon_path(graph: Graph, actor1: str, actor2: str) -> None:
    """Cleanly print out the bacon path between two actors."""
    _, path = bacon_path(graph, actor1, actor2)

    formatted_path = []

    for item in path:
        if isinstance(item, set):
            formatted_path.append(f"[{', '.join(item)}]")
        else:
            formatted_path.append(item)

    print(" -->> ".join(formatted_path))


def bacon_number(graph: Graph, actor1: str, actor2: str) -> int:
    """Given the name of two actors, calculate their bacon number (the shortest path between them)

    >>> g = Graph()
    >>> g.add_vertex('Kevin Bacon', 'actor')
    >>> g.add_vertex('John Cena', 'actor')
    >>> g.add_vertex('Dwayne Johnson', 'actor')
    >>> g.add_edge('Kevin Bacon', 'John Cena')
    >>> g.add_edge('John Cena', 'Dwayne Johnson')
    >>> bacon_number(g, 'Kevin Bacon', 'Kevin Bacon')
    0
    >>> bacon_number(g, 'Kevin Bacon', 'Dwayne Johnson')
    2
    """
    path, _ = bacon_path(graph, actor1, actor2)
    return len(path) - 1


def average_bacon_number(graph: Graph, actor: str) -> int:
    """Given the name of an actor find their average bacon number with all other actors in the graph"""
    actors = graph.get_all_vertices()

    sum_bacon_numbers = 0
    total_bacon_numbers = 0
    for target_actor in actors:
        sum_bacon_numbers += bacon_number(graph, actor, target_actor)
        total_bacon_numbers += 1

    return sum_bacon_numbers // total_bacon_numbers


def compute_average_bacon_number(graph_name: str) -> dict:
    """Compute a full dictionary of actors and their average bacon_numbers for a given dataset."""
    graph, _ = graph_create.initialize_graphs(graph_name)
    actors = graph.get_all_vertices('actor')
    bacon_numbers = {}
    for actor in actors:
        bacon_numbers[actor] = average_bacon_number(graph, actor)

    return bacon_numbers
