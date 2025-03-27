"""Functions for creating the graph"""
from __future__ import annotations
from graph_entities import Graph
import csv


def initialize_graphs(dataset: str) -> tuple[Graph(), dict]:
    """Creates the actor graph and movies dictionary from the given dataset.
    actor_graph is a graph linking actors to actors using movies as the vertices
    movies is a dictionary with movie names as the keys and a tuple containing
    ({cast}, year, votes, rating) as the values"""

    movies = load_csv_file(dataset)
    actor_graph = create_actor_graph(movies)
    return actor_graph, movies


def load_csv_file(dataset: str) -> dict:
    """loads data from csv file"""

    movies = {}
    with open(dataset, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if row[1] not in movies:
                movies[row[1]] = ({row[0]}, (row[2], row[3], row[4]))  # Tuple containing ({cast}, year, votes, rating)
            else:
                movies[row[1]][0].add(row[0])
    return movies


def create_actor_graph(movies: dict) -> Graph:
    """Creates the actor graph.
    Each vertex in the graph is an actor, and each edge is every movie both actors have appeared in."""

    graph = Graph()

    for movie in movies:
        for actor in movies[movie][0]:
            graph.add_vertex(actor, 'actor')
            graph.add_appearences(actor, movie)
            for actor2 in movies[movie][0]:
                if graph.item_in_graph(actor2) and actor != actor2:
                    graph.add_edge(actor, actor2)

    return graph


def create_bacon_actor_graph(movies: dict, path: list) -> Graph:
    """Creates a graph displaying actors in a given bacon path"""
    graph = Graph()

    for actor in path:
        graph.add_vertex(actor, 'actor')

    for i in range(len(path) - 1):
        graph.add_edge(path[i], path[i + 1])

    return graph


def create_recomended_movie_graph(recomendations: list, movies: dict) -> Graph():
    """Creates a graph based on the movie recomendation list
    Each vertex in the graph is a movie, and each edge in the graph is the actors that appear in both movies
    Also adds each movie's cast, year, votes, and rating to the _Vertex object"""

    graph = Graph()

    for i in range(len(recomendations)):
        graph.add_vertex(recomendations[i], 'movie')
        graph.add_movie_info(recomendations[i], movies[recomendations[i]][0], movies[recomendations[i]][1])
        for j in range(0, i):
            graph.add_edge(recomendations[i], recomendations[j])
    return Graph


def create_dict_from_csv(dataset: str) -> dict[str, float]:
    """Creates a dictionary from a CSV file."""
    actor_dict = {}

    with open(dataset, mode='r') as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            actor = row[0]
            rating = float(row[1])
            actor_dict[actor] = rating

    sorted_actor_dict = dict(sorted(actor_dict.items(), key=lambda item: item[1]))

    return sorted_actor_dict
