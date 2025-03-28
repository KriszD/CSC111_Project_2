"""Running the program"""
from typing import Any

from graph_entities import Graph
import graph_create


###################
# Bacon Number
###################

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

    if not path:
        return [], []

    path_with_movies.append(path[-1])  # add back the final actor

    return path, path_with_movies


def bacon_path_filtered(graph: Graph, actor1: str, actor2: str, key: str, lower: int,
                        upper: int, movies: dict) -> tuple[list, list]:
    """Given the names of two actors, find the shortest path between them using filtering.

    Preconditions:
        - key in {'year', 'rating'}
    """
    actors = graph.get_all_vertices('actor')

    if actor1 not in actors or actor2 not in actors:
        print("At least one of those actors is not in this graph.")
        raise ValueError

    path = graph.shortest_path_bfs_filtered(actor1, actor2, key, lower, upper, movies)
    path_with_movies = []

    for i in range(len(path) - 1):
        path_with_movies.append(path[i])  # Add actor
        movies_between = graph.get_common_movies(path[i], path[i + 1])  # Get shared movies
        path_with_movies.append(movies_between)  # Add movie(s)

    if not path:
        return [], []

    path_with_movies.append(path[-1])  # Add final actor

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
    averages = {}

    for actor in actors:
        averages[actor] = average_bacon_number(graph, actor)

    return averages


def ranking(data: dict[str, float], limit: int) -> None:
    """Print out the ranking of <limit> actors based on their average bacon numbers."""
    i = 0
    for actor, avg in data.items():
        if i == limit:
            return
        if avg > 1:
            print(i + 1, ":", actor, "with average bacon number:", avg)
            i += 1


###################
# Movie Similarity
###################

def get_similarity_score_dict(movies: dict, movie1: str, movie2: str) -> float:
    """Returns the similarity score between two movies in a dict"""

    if movies[movie1][0] == set() or movies[movie2][0] == set():
        return 0

    sim_intersection = movies[movie1][0].intersection(movies[movie2][0])
    sim_union = movies[movie1][0].union(movies[movie2][0])
    return len(sim_intersection) / len(sim_union)


def get_recommendations_filtered(movies: dict, input_movie: Any, limit: int, key: str = '',
                                 lower: float = 0, upper: float = 0) -> dict[Any, Any] | list[Any]:
    """Get movie recommendations given an input movie.

    Preconditions:
    - key in {'rating', 'release date'} or key == ''
    """
    recommendations = {}

    if key == '':
        for movie in movies:
            if movie != input_movie:
                sim_score = get_similarity_score_dict(movies, input_movie, movie)
                if sim_score > 0:
                    recommendations[movie] = sim_score

        sorted_recommendations = sorted(recommendations, key=recommendations.get, reverse=True)
        return sorted_recommendations[:limit]

    if key in {'rating', 'release date'}:
        for movie in movies:
            if movie != input_movie and similarity_filter(movies, movie, key, lower, upper):
                sim_score = get_similarity_score_dict(movies, input_movie, movie)
                if sim_score > 0:
                    recommendations[movie] = sim_score

        sorted_recommendations = sorted(recommendations, key=recommendations.get, reverse=True)

        i = 2 if key == 'rating' else 0

        final_recommendations = {}
        for movie in sorted_recommendations[:limit]:
            final_recommendations[movie] = movies[movie][1][i]

        return final_recommendations

    raise ValueError


def similarity_filter(movies: dict, input_movie: str, key: str, lower: float, upper: float) -> bool:
    """Returns whether the given movie's info is within the given bound

    Preconditions:
    - key in {'rating', 'release date'}
    """

    if key == 'rating':
        return lower <= float(movies[input_movie][1][2]) <= upper
    elif key == 'release date':
        return lower <= float(movies[input_movie][1][0]) <= upper
    else:
        raise KeyError


if __name__ == '__main__':
    actor_graph, movie_dict = graph_create.initialize_graphs('Datasets/full_dataset.csv')
    average_bacon_numbers = graph_create.create_dict_from_csv('Datasets/average_bacon_numbers.csv')
    f = get_recommendations_filtered(movie_dict, 'Separate Tables', 25, 'release date', 1960, 2000)
    # running = True
    # menu = ['(1) Bacon Number Ranking', '(2) Average Bacon Number of an actor',
    #         '(3) Bacon Number/Path between two actors', '(4) Bacon Number/Path between two actors (filtered)',
    #         '(5) Exit']
    # while running:
    #     print('Your options are: ', menu)
    #     choice = int(input("What is your choice?"))
    #     if choice not in [1, 2, 3, 4]:
    #         print("Invalid Choice, try Again.")
    #     if choice == 1:
    #         limit = int(input("How many actors? "))
    #         ranking(average_bacon_numbers, limit)
    #     if choice == 2:
    #         actor = str(input("Actor Name: "))
    #         print(actor, "'s Average Bacon Number is:", average_bacon_number(actor_graph, actor))
    #     if choice == 3:
    #         actor1 = str(input("Actor 1 Name: "))
    #         actor2 = str(input("Actor 2 Name: "))
    #         print("The Bacon Number between", actor1, "and", actor2, "is:", bacon_number(actor_graph, actor1, actor2))
    #         print("A path between them is: ")
    #         print_bacon_path(actor_graph, actor1, actor2)
    #     if choice == 4:
    #         print("Bye!")
    #         running = False
