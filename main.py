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


###################
# Movie Similarity
###################

def get_similarity_score(item1: Any, item2: Any) -> float:
    """Return the similarity score between the two movies."""
    if item1.cast_members == 0 or item2.cast_members == 0:
        return 0
    else:
        sim_intersection = item1.cast_members.intersection(item2.cast_members)
        sim_union = item1.cast_members.union(item2.cast_members)
        return len(sim_intersection) / len(sim_union)


def recommend_movies(movies: dict, input_movie: Any, limit: int) -> list[Any]:
    """Get movie recommendations given an input movie."""
    recommendations = {}
    for movie in movies:
        if movie != input_movie:
            sim_score = get_similarity_score(input_movie, movie)
            if sim_score > 0:
                recommendations[movie] = sim_score

    sorted_recommendations = sorted(recommendations, key=recommendations.get, reverse=True)
    return sorted_recommendations[:limit]


def sort_by_closeness(unsorted_dict: dict, value: float, threshold: float) -> list[Any]:
    """Sorting a dictionary into a list based on absolute difference"""
    filtered_items = {k: v for k, v in unsorted_dict.items() if abs(v - value) <= threshold}
    sorted_keys = sorted(filtered_items, key=lambda k: abs(filtered_items[k] - value))

    return sorted_keys


def recommend_movies_filter(movies: dict, input_movie: str, limit: int, movie_filter: str, range_of_filter: float) -> list[str]:
    """Return a list of up to <limit> recommended movies based on similarity to the given movie where the movies
    have gone through a filter that filters movies based on some criteria.

    Preconditions:
        - movie in self._vertices
        - self._vertices[movie].kind == 'movie'
        - limit >= 1
        - filter in {'rating', 'release date'}
    """
    if input_movie not in movies or movies[input_movie].kind != 'movie':
        raise ValueError

    if movie_filter not in {'rating', 'release date'}:
        raise ValueError

    recommendations = recommend_movies(movies, input_movie, limit)
    movie_info_index = 2 if movie_filter == 'rating' else 0
    movie_value = movies[input_movie].movie_info[movie_info_index]

    new_recommendations = {
        recommendation: movies[recommendation].movie_info[movie_info_index]
        for recommendation in recommendations
    }

    sorted_recommendations = sort_by_closeness(new_recommendations, movie_value, range_of_filter)

    return sorted_recommendations[:limit]


if __name__ == '__main__':
    actor_graph, _ = graph_create.initialize_graphs('Datasets/full_dataset.csv')
    average_bacon_numbers = graph_create.create_dict_from_csv('Datasets/average_bacon_numbers.csv')
    # running = True
    # menu = ['(1) Bacon Number Ranking', '(2) Average Bacon Number of an actor',
    #         '(3) Bacon Number between two actors', '(4) Exit']
    # while running:
    #     choice = int(input("What is your choice?"))
    #     if choice not in [1, 2, 3, 4]:
    #         print("Invalid Choice, try Again.")
    #     if choice == 1:
    #         limit = input(int("How many actors? "))
    #         ranking(actor_graph, limit)
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
