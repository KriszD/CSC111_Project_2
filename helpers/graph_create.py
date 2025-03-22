"""Functions for creating the graph"""
from __future__ import annotations
from graph_entities import Graph
from graph_entities import _Vertex
from typing import Any
import csv


def create_actor_graph(dataset: str) -> Graph:
    """Creates the actor graph"""

    graph = Graph()
    casts = {}
    movies = {}
    with open(dataset, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] not in casts:
                casts[row[1]] = {row[0]}
                movies[row[1]] = (row[3], row[4], row[5])  # Tuple containing (year, votes, rating)
            else:
                casts[row[1]].add(row[0])

    for movie in casts:
        for actor in casts[movie]:
            graph.add_vertex(actor, 'actor')
