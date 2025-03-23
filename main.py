"""Running the program"""
from graph_entities import Graph


def bacon_number(graph: Graph, actor1: str, actor2: str) -> int:
    """Given the name of two actors, calculate their bacon number (the shortest path between them)

    >>> g = Graph()
    >>> g.add_vertex('Kevin Bacon', 'actor')
    >>> g.add_vertex('John Cena', 'actor')
    >>> g.add_vertex('Dwayne Johnson', 'actor')
    >>> g.add_edge('Kevin Bacon', 'John Cena')
    >>> g.add_edge('John Cena', 'Dwayne Johnson')
    >>> bacon_number(g, 'Kevin Bacon', 'Kevin Bacon')
    >>> bacon_number(g, 'Kevin Bacon', 'Dwayne Johnson')
    """
    path = graph.shortest_path(actor1, actor2)
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
