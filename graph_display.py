"""Functions for diplaying the graph"""
from plotly.graph_objs import Scatter, Figure
import networkx as nx
from graph_entities import Graph


def visualize_graph(graph: Graph(), max_vertices: int = 5000) -> None:
    """Uses plotly and networkx to visualize the given graph."""
    graph_nx = graph.to_networkx(max_vertices)
