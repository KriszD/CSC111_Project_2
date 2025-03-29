"""Running the program"""
from typing import Any

import python_ta

from graph_entities import Graph
import graph_create
import graph_display


#######################################################################################################################
# Bacon Number
#######################################################################################################################

def bacon_path(graph: Graph, actor1: str, actor2: str, movies: dict = None, key: str = '',
               lower: float = 0, upper: float = 0) -> tuple[list, list]:
    """Given the names of two actors, find the shortest path between in a graph them.

    If not given parameters for filtering, do it using the default method. Otherwise, use the filtering parameters to
    properly filter the shortest path based on those filters.

    Preconditions:
        - key in {'rating', 'release date'} or key == ''
    """
    if movies is None:
        movies = {}
    actors = graph.get_all_vertices('actor')

    if actor1 not in actors or actor2 not in actors:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    path = graph.shortest_path_bfs(actor1, actor2)
    path_with_movies = []

    if key in {'rating', 'release date'}:
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


def print_bacon_path(graph: Graph, actor1: str, actor2: str, movies: dict = None, key: str = '',
                     lower: float = 0, upper: float = 0) -> None:
    """Cleanly print out the bacon path between two actors.

    Note: the filtering parameters are passed in case the function bacon_path needs them, since this function
    relies on bacon_path."""
    if movies is None:
        movies = {}
    actors = graph.get_all_vertices('actor')

    if actor1 not in actors or actor2 not in actors:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    _, path = bacon_path(graph, actor1, actor2, movies, key, lower, upper)

    formatted_path = []

    for item in path:
        if isinstance(item, set):
            formatted_path.append(f"[{', '.join(item)}]")
        else:
            formatted_path.append(item)

    print(" -->> ".join(formatted_path))


def bacon_number(graph: Graph, actor1: str, actor2: str, movies: dict = None, key: str = '',
                 lower: float = 0, upper: float = 0) -> int:
    """Given the name of two actors, calculate their bacon number (the shortest path between them).

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
    if movies is None:
        movies = {}
    actors = graph.get_all_vertices('actor')

    if actor1 not in actors or actor2 not in actors:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    path, _ = bacon_path(graph, actor1, actor2, movies, key, lower, upper)
    return len(path) - 1


def average_bacon_number(graph: Graph, actor: str) -> float:
    """Given an actor's name, find their average Bacon number by finding their shortest path (if possible)
    to all other actors, and taking the average."""
    if actor not in graph.get_all_vertices('actor'):
        raise ValueError("This is not a valid name OR this actor is not in our dataset.")

    distances = graph.shortest_distance_bfs(actor)

    total_distance = sum(dist for dist in distances.values() if dist != float("inf"))
    total_reachable = sum(1 for dist in distances.values() if dist != float("inf"))

    return total_distance / total_reachable if total_reachable > 0 else float("inf")


def compute_average_bacon_numbers(graph: Graph) -> dict:
    """Compute the average Bacon number for every actor in the graph and store it in a dictionary."""
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
        if avg > 0:
            print(i + 1, ":", actor, "with average bacon number:", avg)
            i += 1


#######################################################################################################################
# Movie Similarity
#######################################################################################################################

def get_similarity_score_dict(movies: dict, movie1: str, movie2: str) -> float:
    """Returns the similarity score between two movies based on dividing the intersection of their cast members
    by the union of their cast members."""
    if movie1 not in movies or movie2 not in movies:
        raise ValueError("At least one of these is not a valid name OR is not in our dataset.")

    if movies[movie1][0] == set() or movies[movie2][0] == set():
        return 0

    sim_intersection = movies[movie1][0].intersection(movies[movie2][0])
    sim_union = movies[movie1][0].union(movies[movie2][0])
    return len(sim_intersection) / len(sim_union)


def get_recommendations(movies: dict, input_movie: Any, limit: int, key: str = '',
                        lower: float = 0, upper: float = 0) -> dict[Any, Any] | list[Any]:
    """Get movie recommendations given an input movie.

    Preconditions:
    - key in {'rating', 'release date'} or key == ''
    """
    if input_movie not in movies:
        raise ValueError("This is not a valid name OR this movie is not in our dataset.")

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
            final_recommendations[movie] = key + ' = ' + str(movies[movie][1][i])

        return final_recommendations

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


if __name__ == '__main__':
    # python_ta.check_all(config={
    #     'extra-imports': ['graph_entities', 'graph_create'],  # the names (strs) of imported modules
    #     'allowed-io': ['print_bacon_path', 'ranking'],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

    actor_graph, movie_dict = graph_create.initialize_graphs('Datasets/full_dataset.csv')
    average_bacon_numbers = graph_create.create_dict_from_csv('Datasets/average_bacon_numbers.csv')
    average_bacon_numbers_no_zeroes = {actor: score for actor, score in average_bacon_numbers.items() if score != 0}

    # the meaningful numbers based on OUR dataset.
    average_bacon_numbers_meaningful = {actor: score for actor, score in average_bacon_numbers.items() if score > 1.5}

    running = True
    menu = ['(1) Bacon Number Ranking', '(2) Average Bacon Number of an actor',
            '(3) Bacon Number/Path between two actors', '(4) Movie Recommendations for a movie', '(5) Exit']

    while running:
        print('======================================================================================')
        print('Your options are: ', menu)
        choice = int(input("Your choice: "))

        if choice not in [1, 2, 3, 4, 5]:
            print("Invalid Choice, try Again.")

        if choice == 1:
            limit = int(input("Number of actors: "))
            ranking(average_bacon_numbers, limit)

        if choice == 2:
            actor = str(input("Actor Name: "))
            print("The Average Bacon Number for", actor, "is:", average_bacon_number(actor_graph, actor))
            print("The actor is number", list(average_bacon_numbers_no_zeroes.keys()).index(actor) + 1, "out of",
                  len(average_bacon_numbers_no_zeroes), "in the overall rankings.")

        if choice == 3:
            actor1 = str(input("Actor 1 Name: "))
            actor2 = str(input("Actor 2 Name: "))
            key = str(input("Optional Filters: release date, rating. Type NO if you do not want it to be filtered. "))

            if key != 'NO':
                lower = float(input("Lower bound for filtering: "))
                upper = float(input("Upper bound for filtering: "))
                num = bacon_number(actor_graph, actor1, actor2, movie_dict, key, lower, upper)
                if num < 0:
                    print("These actors share no path.")
                else:
                    print("The Bacon Number between", actor1, "and", actor2, "is:", num)
                    print("A path between them is: ")
                    print_bacon_path(actor_graph, actor1, actor2, movie_dict, key, lower, upper)
                path, _ = bacon_path(actor_graph, actor1, actor2, movie_dict, key, lower, upper)

            else:
                num = bacon_number(actor_graph, actor1, actor2, movie_dict)
                if num < 0:
                    print("These actors share no path.")
                else:
                    print("The Bacon Number between", actor1, "and", actor2, "is:", num)
                    print("A path between them is: ")
                    print_bacon_path(actor_graph, actor1, actor2, movie_dict)
                path, _ = bacon_path(actor_graph, actor1, actor2)

            graph_display.visualize_actor_path(actor_graph, path, (actor1, actor2))

        if choice == 4:
            movie = str(input("Movie Name: "))
            limit = int(input("Number of Recommendations: "))
            key = str(input("Optional Filters: release date, rating. Type NO if you do not want it to be filtered. "))

            if key != 'NO':
                lower = float(input("Lower bound for filtering: "))
                upper = float(input("Upper bound for filtering: "))
                print("Recommended Movies: ", get_recommendations(movie_dict, movie, limit, key, lower, upper))

            else:
                print("Recommended Movies: ", get_recommendations(movie_dict, movie, limit))

        if choice == 5:
            print("Bye! We hope you enjoyed our project! :)")
            running = False
