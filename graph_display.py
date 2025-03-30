"""Functions for diplaying the graph"""

from typing import Any
import networkx as nx
import python_ta
from plotly.graph_objs import Scatter, Figure
from graph_entities import Graph

COLOUR_SCHEME = [
    '#2E91E5', '#E15F99', '#1CA71C', '#FB0D0D', '#DA16FF', '#222A2A', '#B68100',
    '#750D86', '#EB663B', '#511CFB', '#00A08B', '#FB00D1', '#FC0080', '#B2828D',
    '#6C7C32', '#778AAE', '#862A16', '#A777F1', '#620042', '#1616A7', '#DA60CA',
    '#6C4516', '#0D2A63', '#AF0038'
]

LINE_COLOR = 'rgb(210,210,210)'
VERTEX_BORDER_COLOR = 'rgb(50,50,50)'
ACTOR_COLOR = 'rgb(105, 89, 205)'
MOVIE_COLOR = 'rgb(89, 205, 105)'


def visualize_actor_path(graph: Graph, path: list[str], fallback_actors: tuple[str, str] = None,
                         layout: str = 'spring_layout', output_file: str = '') -> None:
    """
    Visualizes a path of actors (and the movies connecting them) using Plotly.

    If the provided path is empty (i.e., no connection between the two actors),
    the function will display only the two actors (from fallback_actors) as nodes with no connecting edge.

    Parameters:
        graph: The custom graph (an instance of Graph from graph_entities).
        path: A list of actor names representing the path.
        fallback_actors: A tuple containing the two actor names to display when path is empty.
        layout: The NetworkX layout algorithm to use (e.g., 'spring_layout').
        output_file: If provided, the Plotly figure is saved to this file; otherwise, it is displayed.
    """
    # If no path is found, and fallback actors are provided, use them.
    used_fallback_actors = False
    if not path:
        if fallback_actors is not None:
            path = list(fallback_actors)
            used_fallback_actors = True
        else:
            print("No path found and no fallback actors provided.")
            return

    # Create a new NetworkX graph to represent the actor path.
    g = nx.Graph()

    # Add nodes for each actor in the path.
    for actor in path:
        g.add_node(actor, kind='actor')

    # Only add edges if a path was actually found (i.e. if fallback actors are not used)
    if len(path) > 1 and graph.get_common_movies(path[0], path[1]) and not used_fallback_actors:
        for i in range(len(path) - 1):
            actor1 = path[i]
            actor2 = path[i + 1]
            common_movies = graph.get_common_movies(actor1, actor2)
            movies_str = '<br>'.join(sorted(common_movies)) if common_movies else ''
            g.add_edge(actor1, actor2, movies=movies_str)

    # Compute node positions using the selected layout algorithm.
    pos = getattr(nx, layout)(g)

    # Extract node coordinates and labels.
    x_values = [pos[node][0] for node in g.nodes()]
    y_values = [pos[node][1] for node in g.nodes()]
    labels = list(g.nodes())

    # Calculate buffer margins for the canvas border
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    buffer_x = (max_x - min_x) * 0.20
    buffer_y = (max_y - min_y) * 0.20

    # Compute a scaling factor based on the average range.
    avg_range = ((max_x - min_x) + (max_y - min_y)) / 2.0
    if avg_range != 0:
        scale = avg_range / 3
    else:
        scale = 1

    # Set base sizes for nodes, fonts, and edges.
    base_node_size = 50
    base_node_font = 50
    base_edge_font = 40
    base_edge_width = 3

    # Apply scaling.
    node_size = max(base_node_size * scale, 1)
    node_font_size = max(base_node_font * scale, 1)
    edge_font_size = max(base_edge_font * scale, 1)
    edge_width = max(base_edge_width * scale, 1)

    # Prepare the edge coordinates.
    x_edges = []
    y_edges = []
    for edge in g.edges():
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    # Create a scatter trace for edges.
    edge_trace = Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        name='edges',
        line={"color": 'rgb(210,210,210)', "width": edge_width},
        hoverinfo='none'
    )

    # Create a scatter trace for nodes.
    actor_color = 'rgb(105,89,205)'
    node_trace = Scatter(
        x=x_values,
        y=y_values,
        mode='markers+text',
        text=labels,
        textposition='top center',
        textfont={"size": node_font_size},  # Dynamically scaled node label size
        marker={"symbol": 'circle',
                "size": node_size,
                "color": actor_color,
                "line": {"color": 'rgb(50,50,50)', "width": 1}},
        hovertemplate='%{text}',
        hoverlabel={'namelength': 0}
    )

    # Create a scatter trace for edge labels.
    edge_label_x = []
    edge_label_y = []
    edge_labels = []
    for edge in g.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)
        edge_labels.append(edge[2].get('movies', ''))

    edge_label_trace = Scatter(
        x=edge_label_x,
        y=edge_label_y,
        mode='text',
        text=edge_labels,
        textposition='middle center',
        textfont={"size": edge_font_size},  # Dynamically scaled edge label size
        hoverinfo='none'
    )

    # Build the figure.
    fig = Figure(data=[edge_trace, node_trace, edge_label_trace])
    fig.update_layout(
        showlegend=False,
        xaxis={"showgrid": False, "zeroline": False, "visible": False,
               "range": [min_x - buffer_x, max_x + buffer_x]},
        yaxis={"showgrid": False, "zeroline": False, "visible": False,
               "range": [min_y - buffer_y, max_y + buffer_y]}
    )

    # Display or save the figure.
    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()


def add_movie_node(graph_nx: nx.Graph, vertex: Any, max_vertices: int) -> None:
    """Add a movie node to graph_nx if it's not already present and we haven't exceeded max_vertices.

    vertex is a _Vertex object with attributes item, kind, and optionally sim_score.
    """
    if graph_nx.number_of_nodes() < max_vertices and vertex.item not in graph_nx.nodes:
        graph_nx.add_node(vertex.item,
                          kind=vertex.kind,
                          label=f"{vertex.item}",
                          sim=getattr(vertex, 'sim_score', 0))


def get_edge_sim_label(v: Any, u: Any) -> str:
    """
    Determine the edge similarity label between two vertices.
    If one vertex is the main movie (sim_score == 1) and the other is not,
    returns the recommended movie's sim_score as a string formatted to three decimal places;
    otherwise, returns an empty string.
    """
    v_sim = getattr(v, 'sim_score', None)
    u_sim = getattr(u, 'sim_score', None)
    if v_sim is not None and u_sim is not None:
        if v_sim == 1 and u_sim != 1:
            return f"{u_sim:.3f}"
        elif u_sim == 1 and v_sim != 1:
            return f"{v_sim:.3f}"
    return ""


def movie_graph_to_networkx(movie_graph: Graph, max_vertices: int = 5000) -> nx.Graph:
    """
    Convert a custom movie graph (an instance of Graph) into a NetworkX graph.
    Only includes up to max_vertices nodes.

    This function assumes that movie_graph._vertices is a dictionary where each value
    is a _Vertex object that has attributes such as item (movie name), kind, and optionally
    sim_score (set by add_sim_score). The main movie should have a sim_score of 1.
    """
    graph_nx = nx.Graph()
    for v in movie_graph.get_vertices().values():
        if graph_nx.number_of_nodes() >= max_vertices:
            break
        # Add the main movie node.
        graph_nx.add_node(v.item, kind=v.kind, label=f"{v.item}", sim=getattr(v, 'sim_score', 0))

        for u in v.neighbours:
            add_movie_node(graph_nx, u, max_vertices)
            # Compute edge similarity label.
            edge_label = get_edge_sim_label(v, u)
            if u.item in graph_nx.nodes:
                graph_nx.add_edge(v.item, u.item, sim=edge_label)

    return graph_nx


def visualize_movie_graph(movie_graph: Graph, layout: str = 'spring_layout',
                          max_vertices: int = 5000, output_file: str = '') -> None:
    """
    Visualizes the custom movie graph using Plotly.
    Each node's size is determined by a fixed base size multiplied by its similarity score.

    Parameters:
        movie_graph: A custom Graph object for movies (as returned by create_recommended_movie_graph).
        layout: Which NetworkX layout algorithm to use (default 'spring_layout').
        max_vertices: Maximum number of vertices to include in the visualization.
        output_file: If provided, the Plotly figure is saved to this file; otherwise, it is displayed.
    """
    # Convert the custom movie graph to a NetworkX graph.
    graph_nx = movie_graph_to_networkx(movie_graph, max_vertices)

    # Compute positions for all nodes using the selected layout algorithm.
    pos = getattr(nx, layout)(graph_nx)

    # Extract node positions and labels.
    x_values = [pos[n][0] for n in graph_nx.nodes]
    y_values = [pos[n][1] for n in graph_nx.nodes]
    labels = [graph_nx.nodes[n].get('label', n) for n in graph_nx.nodes]

    # Set a fixed base node size for the main movie.
    base_main_size = 30

    # Compute node sizes: size = base_main_size * sim_score.
    # The main movie should have a sim_score of 1.
    node_sizes = []
    for node in graph_nx.nodes:
        sim_val = graph_nx.nodes[node].get('sim', 1)  # default sim=1 for main movie.
        node_sizes.append(base_main_size * (0.5 + sim_val))

    # Prepare the edge coordinates.
    x_edges = []
    y_edges = []
    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    # Create a scatter trace for edges.
    edge_trace = Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        name='edges',
        line={"color": LINE_COLOR, "width": 3},
        hoverinfo='none'
    )

    # Create a scatter trace for nodes.
    node_trace = Scatter(
        x=x_values,
        y=y_values,
        mode='markers+text',
        text=labels,
        textposition='top center',
        textfont={"size": 20},
        marker={"symbol": 'circle',
                "size": node_sizes,
                "color": MOVIE_COLOR,
                "line": {"color": VERTEX_BORDER_COLOR, "width": 1}},
        hovertemplate='%{text}',
        hoverlabel={'namelength': 0}
    )

    # Optionally, add edge labels (if needed, for similarity scores).
    edge_label_x = []
    edge_label_y = []
    edge_labels = []
    for edge in graph_nx.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)
        edge_labels.append(str(edge[2].get('sim', '')))

    edge_label_trace = Scatter(
        x=edge_label_x,
        y=edge_label_y,
        mode='text',
        text=edge_labels,
        textposition='middle center',
        textfont={"size": 15},
        hoverinfo='none'
    )

    # Calculate buffer margins for the canvas border.
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    buffer_x = (max_x - min_x) * 0.30
    buffer_y = (max_y - min_y) * 0.30

    # Build and configure the Plotly figure.
    fig = Figure(data=[edge_trace, node_trace, edge_label_trace])
    fig.update_layout(
        showlegend=False,
        xaxis={"showgrid": False, "zeroline": False, "visible": False,
               "range": [min_x - buffer_x, max_x + buffer_x]},
        yaxis={"showgrid": False, "zeroline": False, "visible": False,
               "range": [min_y - buffer_y, max_y + buffer_y]}
    )

    # Display or save the figure.
    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()


if __name__ == '__main__':
    python_ta.check_all(config={
        'extra-imports': ['networkx', 'plotly.graph_objs', 'graph_entities'],  # the names (strs) of imported modules
        'allowed-io': ['visualize_actor_path'],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
