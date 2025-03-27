"""Running the program"""
from graph_entities import Graph
import graph_create


def bacon_path(graph: Graph, actor1: str, actor2: str) -> tuple[list, list]:
    """Given the name of two actors, find the path between them, return two lists, one with movies and one without"""
    actors = graph.get_all_vertices('actor')
    if actor1 not in actors or actor2 not in actors:
        print("At least one of those actors is not in this graph.")
        raise ValueError
    path = graph.shortest_path_bfs(actor1, actor2)
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


def average_bacon_number(graph: Graph, actor: str) -> float:
    """Given an actor's name, find their average Bacon number with all other actors in the graph."""
    distances = graph.shortest_distance_bfs(actor)

    total_distance = sum(dist for dist in distances.values() if dist != float("inf"))
    total_reachable = sum(1 for dist in distances.values() if dist != float("inf"))

    return total_distance / total_reachable if total_reachable > 0 else float("inf")


def compute_average_bacon_numbers(graph: Graph) -> dict:
    """Compute the average Bacon number for every actor in the graph."""
    actors = graph.get_all_vertices('actor')
    average_bacon_numbers = {}

    for actor in actors:
        average_bacon_numbers[actor] = graph.average_bacon_number(actor)

    return average_bacon_numbers


if __name__ == '__main__':
    actor_graph, _ = graph_create.initialize_graphs('Datasets/full_dataset.csv')
    # running = True
    # menu = ['(1) Bacon Number Ranking', '(2) Average Bacon Number of an actor',
    #         '(3) Bacon Number between two actors', '(4) Exit']
    # while running:
    #     choice = int(input("What is your choice?"))
    #     if choice not in [1, 2, 3, 4]:
    #         print("Invalid Choice, try Again.")
    #     if choice == 1:
    #         pass
    #     if choice == 2:
    #         actor = str(input("Actor Name: "))
    #         print(actor, "'s Average Bacon Number is:", average_bacon_number(actor_graph, actor))
    #     if choice == 3:
    #         actor1 = str(input("Actor 1 Name: "))
    #         actor2 = str(input("Actor 2 Name: "))
    #         print("The Bacon Number between", actor1, "and", actor2, "is:", bacon_number(actor_graph, actor1, actor2))
    #     if choice == 4:
    #         print("Bye!")
    #         running = False

