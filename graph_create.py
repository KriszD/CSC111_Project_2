"""Functions for creating the graph"""
from __future__ import annotations
from graph_entities import Graph
import csv


def create_full_graph(dataset: str) -> tuple:
    """Creates the actor and movie graphs from the given dataset"""
    casts, movies = load_csv_file(dataset)
    actor_graph = create_actor_graph(casts)
    # movie_graph = create_movie_graph ....
    return actor_graph, None


def load_csv_file(dataset: str) -> tuple:
    """loads data from csv file"""

    casts = {}
    movies = {}
    with open(dataset, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] not in casts:
                casts[row[1]] = {row[0]}
                movies[row[1]] = (row[2], row[3], row[4])  # Tuple containing (year, votes, rating)
            else:
                casts[row[1]].add(row[0])
    return casts, movies


def create_actor_graph(casts: dict) -> Graph:
    """Creates the actor graph"""

    graph = Graph()

    for movie in casts:
        for actor in casts[movie]:
            graph.add_vertex(actor, 'actor')
            graph.add_appearences(actor, movie)
            for actor2 in casts[movie]:
                if graph.item_in_graph(actor2) and actor != actor2:
                    graph.add_edge(actor, actor2)

    return graph
