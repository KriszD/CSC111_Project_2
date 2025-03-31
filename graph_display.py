"""Functions for diplaying the graph."""

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

LINE_COLOUR = 'rgb(210,210,210)'
VERTEX_BORDER_COLOUR = 'rgb(50,50,50)'
ACTOR_COLOUR = 'rgb(105, 89, 205)'
MOVIE_COLOUR = 'rgb(89, 205, 105)'


#######################################################################################################################
# General Helper Functions
#######################################################################################################################

def compute_layout_and_scaling(g: nx.Graph, layout: str) -> tuple[dict[any, tuple], float, tuple[float, float]]:
    """
    Computes node positions using the given layout and calculates scaling factors and buffer margins.
    """
    # Compute positions using the chosen layout algorithm
    pos = getattr(nx, layout)(g)

    x_values = [pos[node][0] for node in g.nodes()]
    y_values = [pos[node][1] for node in g.nodes()]

    # Compute canvas buffers
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    buffer_x = (max_x - min_x) * 0.30
    buffer_y = (max_y - min_y) * 0.30

    # Compute a scaling factor based on average range
    avg_range = ((max_x - min_x) + (max_y - min_y)) / 2.0
    scale = avg_range / 3 if avg_range != 0 else 1

    return pos, scale, (buffer_x, buffer_y)


def compute_scaled_parameters(scale: float) -> dict[str, float]:
    """
    Computes scaled parameters for node sizes, fonts, and edge widths.
    """
    base_node_size = 50
    base_node_font = 50
    base_edge_font = 40
    base_edge_width = 3

    return {
        'node_size': max(base_node_size * scale, 1),
        'node_font_size': max(base_node_font * scale, 1),
        'edge_font_size': max(base_edge_font * scale, 1),
        'edge_width': max(base_edge_width * scale, 1)
    }


def create_edge_trace(g: nx.Graph, pos: dict[any, tuple], scaled: dict[str, float]) -> Scatter:
    """
    Creates the Plotly scatter trace for edges.
    """
    x_edges, y_edges = [], []
    for edge in g.edges():
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    return Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        name='edges',
        line={"color": LINE_COLOUR, "width": scaled['edge_width']},
        hoverinfo='none'
    )


def build_figure(edge_trace: Scatter, node_trace: Scatter, edge_label_trace: Scatter,
                 pos: dict[any, tuple], buffers: tuple[float, float]) -> Figure:
    """
    Constructs the Plotly figure with the provided traces and layout settings.

    The figure's axes ranges are adjusted using computed buffer margins.
    """
    x_values = [pos[node][0] for node in pos]
    y_values = [pos[node][1] for node in pos]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    buffer_x, buffer_y = buffers

    fig = Figure(data=[edge_trace, node_trace, edge_label_trace])
    fig.update_layout(
        showlegend=False,
        xaxis={"showgrid": False, "zeroline": False, "visible": False,
               "range": [min_x - buffer_x, max_x + buffer_x]},
        yaxis={"showgrid": False, "zeroline": False, "visible": False,
               "range": [min_y - buffer_y, max_y + buffer_y]}
    )
    return fig


#######################################################################################################################
# Actor Path Visualization
#######################################################################################################################

def get_effective_path(path: list[str], fallback_actors: tuple[str, str] = None) -> tuple[list[str], bool]:
    """
    Returns the effective path to visualize.

    If the provided path is empty and fallback actors are given, the fallback actors are used.
    Returns a tuple containing the path and a boolean flag indicating whether fallback actors were used.
    """
    used_fallback = False
    if not path:
        if fallback_actors is not None:
            path = list(fallback_actors)
            used_fallback = True
    return path, used_fallback


def build_actor_graph(graph: Graph, path: list[str], used_fallback: bool) -> nx.Graph:
    """
    Constructs a NetworkX graph for the actor path.

    Each actor is added as a node, and if a valid path is provided (i.e., fallback not used),
    edges are added based on common movies.
    """
    g = nx.Graph()
    # Add nodes
    for actor in path:
        g.add_node(actor, kind='actor')
    # Add edges only if a real path is found
    if len(path) > 1 and graph.get_common_movies(path[0], path[1]) and not used_fallback:
        for i in range(len(path) - 1):
            actor1 = path[i]
            actor2 = path[i + 1]
            common_movies = graph.get_common_movies(actor1, actor2)
            movies_str = '<br>'.join(sorted(common_movies)) if common_movies else ''
            g.add_edge(actor1, actor2, movies=movies_str)
    return g


def create_node_trace_actor_path(g: nx.Graph, pos: dict[any, tuple], scaled: dict[str, float]) -> Scatter:
    """
    Creates the Plotly scatter trace for nodes for the actor path visualization.
    """
    labels = list(g.nodes())
    x_values = [pos[node][0] for node in g.nodes()]
    y_values = [pos[node][1] for node in g.nodes()]

    return Scatter(
        x=x_values,
        y=y_values,
        mode='markers+text',
        text=labels,
        textposition='top center',
        textfont={"size": scaled['node_font_size']},
        marker={
            "symbol": 'circle',
            "size": scaled['node_size'],
            "color": ACTOR_COLOUR,
            "line": {"color": VERTEX_BORDER_COLOUR, "width": 1}
        },
        hovertemplate='%{text}',
        hoverlabel={'namelength': 0}
    )


def create_edge_label_actor_path(g: nx.Graph, pos: dict[any, tuple], scaled: dict[str, float])\
        -> Scatter:
    """
    Creates the Plotly scatter trace for edge labels for the actor path visualization.
    """
    edge_label_x, edge_label_y, edge_labels = [], [], []
    for edge in g.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)
        edge_labels.append(edge[2].get('movies', ''))

    return Scatter(
        x=edge_label_x,
        y=edge_label_y,
        mode='text',
        text=edge_labels,
        textposition='middle center',
        textfont={"size": scaled['edge_font_size']},
        hoverinfo='none'
    )


def create_traces_actor_path(g: nx.Graph, pos: dict[any, tuple], scale: float)\
        -> tuple[Scatter, Scatter, Scatter]:
    """
    Creates the Plotly scatter traces for edges, nodes, and edge labels for the actor path visualization.

    Scaling is applied to node sizes, fonts, and edge widths.
    """
    scaled = compute_scaled_parameters(scale)
    edge_trace = create_edge_trace(g, pos, scaled)
    node_trace = create_node_trace_actor_path(g, pos, scaled)
    edge_label_trace = create_edge_label_actor_path(g, pos, scaled)

    return edge_trace, node_trace, edge_label_trace


def visualize_actor_path(graph: Graph, path: list[str], fallback_actors: tuple[str, str] = None,
                         layout: str = 'spring_layout', output_file: str = '') -> None:
    """
    Visualizes a path of actors (and the movies connecting them) using Plotly.

    If the provided path is empty, the function will display only the two fallback actors as nodes.
    """
    # Determine the effective path and whether fallback actors were used
    path, used_fallback = get_effective_path(path, fallback_actors)
    if not path:
        return  # Early return if no valid path is available

    # Build the NetworkX graph for the path.
    g = build_actor_graph(graph, path, used_fallback)

    # Compute layout positions and scaling factors.
    pos, scale, buffers = compute_layout_and_scaling(g, layout)

    # Create Plotly traces for edges, nodes, and edge labels.
    edge_trace, node_trace, edge_label_trace = create_traces_actor_path(g, pos, scale)

    # Build the figure with the computed traces and layout.
    fig = build_figure(edge_trace, node_trace, edge_label_trace, pos, buffers)

    # Display or save the figure.
    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()


#######################################################################################################################
# Recommended Movie Graph Visualization
#######################################################################################################################

def add_movie_node(graph_nx: nx.Graph, vertex: any, max_vertices: int) -> None:
    """Add a movie node to graph_nx if it's not already present, and we haven't exceeded max_vertices.
    """
    if graph_nx.number_of_nodes() < max_vertices and vertex.item not in graph_nx.nodes:
        graph_nx.add_node(vertex.item,
                          kind=vertex.kind,
                          label=f"{vertex.item}",
                          sim=getattr(vertex, 'sim_score', 0))


def get_edge_sim_label(v: any, u: any) -> str:
    """
    Determine the edge similarity label between two vertices.
    If one vertex is the main movie (sim_score == 1) and the other is not,
    returns the recommended movie's sim_score as a percentage string (e.g., "22.2%");
    otherwise, returns an empty string.
    """
    v_sim = getattr(v, 'sim_score', None)
    u_sim = getattr(u, 'sim_score', None)
    if v_sim is not None and u_sim is not None:
        if v_sim == 1 and u_sim != 1:
            return f"{u_sim * 100:.1f}%"
        elif u_sim == 1 and v_sim != 1:
            return f"{v_sim * 100:.1f}%"
    return ""


def movie_graph_to_networkx(movie_graph: Graph, max_vertices: int = 5000) -> nx.Graph:
    """
    Convert a custom movie graph (an instance of Graph) into a NetworkX graph.
    Only includes up to max_vertices nodes.
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


def create_node_trace_movie_graph(graph_nx: nx.Graph, pos: dict[any, tuple], base_main_size: float = 30)\
        -> Scatter:
    """
    Extracts node positions and labels, computes node sizes based on similarity scores,
    and returns a Plotly scatter trace for nodes for the movie graph.
    """
    # Extract node positions and labels.
    x_values = [pos[n][0] for n in graph_nx.nodes]
    y_values = [pos[n][1] for n in graph_nx.nodes]
    labels = [graph_nx.nodes[n].get('label', n) for n in graph_nx.nodes]

    # Compute node sizes based on the similarity scores.
    # The main movie has a sim_score of 1.
    node_sizes = []
    for node in graph_nx.nodes:
        sim_val = graph_nx.nodes[node].get('sim', 1)
        node_sizes.append(base_main_size * (0.5 + sim_val))

    # Create and return the scatter trace for nodes.
    node_trace = Scatter(
        x=x_values,
        y=y_values,
        mode='markers+text',
        text=labels,
        textposition='top center',
        textfont={"size": 20},
        marker={"symbol": 'circle',
                "size": node_sizes,
                "color": MOVIE_COLOUR,
                "line": {"color": VERTEX_BORDER_COLOUR, "width": 1}},
        hovertemplate='%{text}',
        hoverlabel={'namelength': 0}
    )
    return node_trace


def create_edge_label_movie_graph(graph_nx: nx.Graph, pos: dict[any, tuple], font_size: int = 15)\
        -> Scatter:
    """
    Creates a Plotly scatter trace for edge labels representing similarity scores for the movie graph.
    """
    edge_label_x = []
    edge_label_y = []
    edge_labels = []
    for edge in graph_nx.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)
        edge_labels.append(str(edge[2].get('sim', '')))

    return Scatter(
        x=edge_label_x,
        y=edge_label_y,
        mode='text',
        text=edge_labels,
        textposition='middle center',
        textfont={"size": font_size},
        hoverinfo='none'
    )


def visualize_movie_graph(movie_graph: Graph, layout: str = 'spring_layout',
                          max_vertices: int = 5000, output_file: str = '') -> None:
    """
    Visualizes the recommended movie graph using Plotly.
    """
    # Convert the custom movie graph to a NetworkX graph.
    graph_nx = movie_graph_to_networkx(movie_graph, max_vertices)

    # Compute positions and canvas buffers using the helper function.
    pos, _, buffers = compute_layout_and_scaling(graph_nx, layout)

    # Compute scaled parameters using a fixed scale of 1.
    scaled = compute_scaled_parameters(1)

    # Create the scatter trace for edges using the helper function.
    edge_trace = create_edge_trace(graph_nx, pos, scaled)

    # Create the scatter trace for nodes using the new helper function.
    node_trace = create_node_trace_movie_graph(graph_nx, pos)

    # Create the scatter trace for edge labels using the new helper function.
    edge_label_trace = create_edge_label_movie_graph(graph_nx, pos)

    # Build the Plotly figure using the build_figure helper.
    fig = build_figure(edge_trace, node_trace, edge_label_trace, pos, buffers)

    # Display or save the figure.
    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['networkx', 'plotly.graph_objs', 'graph_entities'],  # the names (strs) of imported modules
        'allowed-io': ['visualize_actor_path'],  # the names (strs) of functions that call print/open/input
        'max-line-length': 120
    })
