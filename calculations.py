"""All the calculations that are performed for our project."""
from typing import Any

import python_ta
from graph_entities import Graph


#######################################################################################################################
# Bacon Number
#######################################################################################################################

def bacon_path(graph: Graph, actors: tuple[str, str], movies: dict = None, key: str = '',
               thresholds: tuple[float, float] = (0, 0)) -> tuple[list, list]:
    """Given the names of two actors, find the shortest path between in a graph them.

    If not given parameters for filtering, do it using the default method. Otherwise, use the filtering parameters to
    properly filter the shortest path based on those filters.

    Preconditions:
        - key in {'rating', 'release date'} or key == ''
        - movies == None and lower == 0 and upper == 0 or key != ''
    >>> import graph_create
    >>> bp_graph, movies_dict = graph_create.initialize_graphs('datasets/full_dataset.csv')
    >>> bp = bacon_path(bp_graph, ('Fred Astaire', 'Dwayne Johnson'))[0]
    >>> len(bp) == 3
    True
    >>> bp[0] == 'Fred Astaire' and bp[2] == 'Dwayne Johnson'
    True
    """
    if movies is None:
        movies = {}
    other_actors = graph.get_all_vertices('actor')

    actor1, actor2 = actors[0], actors[1]

    if actor1 not in other_actors or actor2 not in other_actors:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    path = graph.shortest_path_bfs(actor1, actor2)
    path_with_movies = []

    if key in {'rating', 'release date'}:
        lower, upper = thresholds[0], thresholds[1]
        path = graph.shortest_path_bfs_filtered((actor1, actor2), key, (lower, upper), movies)
        path_with_movies = []

    for i in range(len(path) - 1):
        path_with_movies.append(path[i])  # Add actor
        movies_between = graph.get_common_movies(path[i], path[i + 1])  # Get shared movies
        path_with_movies.append(movies_between)  # Add movie(s)

    if not path:
        return [], []

    path_with_movies.append(path[-1])  # Add final actor

    return path, path_with_movies


def print_bacon_path(graph: Graph, actors: tuple[str, str], movies: dict = None, key: str = '',
                     thresholds: tuple[float, float] = (0, 0)) -> None:
    """Cleanly print out the bacon path between two actors.

    Note: the filtering parameters are passed in case the function bacon_path needs them, since this function
    relies on bacon_path."""
    if movies is None:
        movies = {}
    other_actors = graph.get_all_vertices('actor')

    actor1, actor2 = actors[0], actors[1]

    if actor1 not in other_actors or actor2 not in other_actors:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    lower, upper = thresholds[0], thresholds[1]
    _, path = bacon_path(graph, (actor1, actor2), movies, key, (lower, upper))

    formatted_path = []

    for item in path:
        if isinstance(item, set):
            formatted_path.append(f"[{', '.join(item)}]")
        else:
            formatted_path.append(item)

    print(" -->> ".join(formatted_path))


def bacon_number(graph: Graph, actors: tuple[str, str], movies: dict = None, key: str = '',
                 thresholds: tuple[float, float] = (0, 0)) -> int:
    """Given the name of two actors, calculate their bacon number (the shortest path between them).

    >>> g = Graph()
    >>> g.add_vertex('Kevin Bacon', 'actor')
    >>> g.add_vertex('John Cena', 'actor')
    >>> g.add_vertex('Dwayne Johnson', 'actor')
    >>> g.add_edge('Kevin Bacon', 'John Cena')
    >>> g.add_edge('John Cena', 'Dwayne Johnson')
    >>> bacon_number(g, ('Kevin Bacon', 'Kevin Bacon'))
    0
    >>> bacon_number(g, ('Kevin Bacon', 'Dwayne Johnson'))
    2
    """
    if movies is None:
        movies = {}
    other_actors = graph.get_all_vertices('actor')

    actor1, actor2 = actors[0], actors[1]

    if actor1 not in other_actors or actor2 not in other_actors:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    lower, upper = thresholds[0], thresholds[1]
    path, _ = bacon_path(graph, (actor1, actor2), movies, key, (lower, upper))
    return len(path) - 1


def average_bacon_number(graph: Graph, actor: str) -> float:
    """Given an actor's name, find their average Bacon number by finding their shortest path (if possible)
    to all other actors, and taking the average.

    Preconditions:
    - actor in graph.get_all_vertices('actor')
    >>> import graph_create
    >>> avg_bn_graph = graph_create.initialize_graphs('datasets/full_dataset.csv')[0]
    >>> average_bacon_number(avg_bn_graph, 'Fred Astaire')
    2.4230608404766882
    >>> average_bacon_number(avg_bn_graph, 'Michele Morrone')
    1.0
    """
    if actor not in graph.get_all_vertices('actor'):
        raise ValueError("This is not a valid name OR this actor is not in our dataset.")

    distances = graph.shortest_distance_bfs(actor)

    total_distance = sum(dist for dist in distances.values() if dist != float("inf"))
    total_reachable = sum(1 for dist in distances.values() if dist != float("inf"))

    return total_distance / total_reachable if total_reachable > 0 else float("inf")


def compute_average_bacon_numbers(graph: Graph) -> dict:
    """Compute the average Bacon number for every actor in the graph and store it in a dictionary.
    """
    actors = graph.get_all_vertices('actor')
    averages = {}

    for actor in actors:
        averages[actor] = average_bacon_number(graph, actor)

    return averages


def ranking(data: dict[str, float], limit: int) -> None:
    """Print out the ranking of <limit> actors based on their average bacon numbers.
    """
    i = 0
    for actor, avg in data.items():
        if i == limit:
            return
        if avg > 0:
            print(i + 1, ":", actor, "with average bacon number:", avg)
            i += 1


#######################################################################################################################
# Movie Similarity
#######################################################################################################################

def get_similarity_score_dict(movies: dict, movie1: str, movie2: str) -> float:
    """Returns the similarity score between two movies based on dividing the intersection of their cast members
    by the union of their cast members.
    """
    if movie1 not in movies or movie2 not in movies:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    if movies[movie1][0] == set() or movies[movie2][0] == set():
        return 0

    sim_intersection = movies[movie1][0].intersection(movies[movie2][0])
    sim_union = movies[movie1][0].union(movies[movie2][0])
    return len(sim_intersection) / len(sim_union)


def get_recommendations(movies: dict, input_movie: Any, limit: int, key: str = '',
                        thresholds: tuple[float, float] = (0, 0)) \
        -> (tuple[dict[Any, Any], dict[str, float]] | tuple[list[Any], dict[str, float]]):
    """Get movie recommendations given an input movie using the similarity score algorithm
    (intersection of cast / union of cast).

    Preconditions:
    - key in {'rating', 'release date'} or key == ''
    """
    if input_movie not in movies:
        raise ValueError("This is not a valid name OR this movie is not in our dataset.")

    recommendations = {}

    if key == '':
        for movie in movies:
            sim_score = get_similarity_score_dict(movies, input_movie, movie)
            if movie != input_movie and sim_score > 0:
                recommendations[movie] = sim_score

        sorted_recommendations = sorted(recommendations, key=recommendations.get, reverse=True)
        return sorted_recommendations[:limit], recommendations

    if key in {'rating', 'release date'}:
        for movie in movies:
            sim_score = get_similarity_score_dict(movies, input_movie, movie)
            lower, upper = thresholds[0], thresholds[1]
            if movie != input_movie and similarity_filter(movies, movie, key, lower, upper) and sim_score > 0:
                recommendations[movie] = sim_score

        sorted_recommendations = sorted(recommendations, key=recommendations.get, reverse=True)

        i = 2 if key == 'rating' else 0

        final_recommendations = {}
        for movie in sorted_recommendations[:limit]:
            if i == 2:
                final_recommendations[movie] = float(movies[movie][1][i])
            elif i == 0:
                final_recommendations[movie] = int(movies[movie][1][i])

        return final_recommendations, recommendations

    raise ValueError


def similarity_filter(movies: dict, input_movie: str, key: str, lower: float, upper: float) -> bool:
    """Returns whether the given movie's info is within the given bound.

    Preconditions:
        - key in {'rating', 'release date'} or key == ''
    """
    if input_movie not in movies:
        raise ValueError("This is not a valid name OR this movie is not in our dataset.")

    if key == 'rating':
        return lower <= float(movies[input_movie][1][2]) <= upper
    elif key == 'release date':
        return lower <= float(movies[input_movie][1][0]) <= upper
    else:
        raise KeyError


#######################################################################################################################
# Extra Functions
#######################################################################################################################

def is_float(s: str) -> bool:
    """Return whether a given string represents a float data type. This includes integers as well.

    >>> a = '1'
    >>> b = '1.5'
    >>> c = 'banana'
    >>> is_float(a)
    True
    >>> is_float(b)
    True
    >>> is_float(c)
    False
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    python_ta.check_all(config={
        'extra-imports': ['graph_entities', 'graph_create'],
        'allowed-io': ['print_bacon_path', 'ranking'],
        'max-line-length': 120
    })
