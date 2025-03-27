"""Functions for diplaying the graph"""

import networkx as nx
from plotly.graph_objs import Scatter, Figure

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


def to_networkx(graph, max_vertices: int = 5000) -> nx.Graph:
    """Converts our custom graph into a NetworkX graph.

    Iterates over all vertices and edges in the custom graph (using its internal _vertices dictionary)
    and adds them to a new NetworkX graph. Limits the total number of vertices to max_vertices.

    Parameters:
        graph: The custom graph (an instance of Graph from graph_entities).
        max_vertices: Maximum number of vertices to include.

    Returns:
        A NetworkX undirected graph.
    """
    G = nx.Graph()
    count = 0
    # Add nodes with their 'kind' attribute
    for item, vertex in graph._vertices.items():
        if count >= max_vertices:
            break
        G.add_node(item, kind=vertex.kind)
        count += 1

    # Add edges between nodes.
    # To avoid duplicates in an undirected graph, we only add an edge if item < neighbour.item.
    for item, vertex in graph._vertices.items():
        for neighbour in vertex.neighbours:
            # Only add if both vertices exist in our networkx graph (in case of vertex limit)
            if item in G.nodes and neighbour.item in G.nodes:
                if item < neighbour.item:
                    G.add_edge(item, neighbour.item)
    return G


def visualize_graph(graph, layout: str = 'spring_layout', max_vertices: int = 5000,
                    output_file: str = '') -> None:
    """Visualizes the given graph using Plotly.

    The function converts the custom graph to a NetworkX graph, computes a layout,
    and then creates two Plotly scatter traces: one for edges and one for nodes.

    Parameters:
        graph: The custom graph (an instance of Graph from graph_entities).
        layout: The NetworkX layout algorithm to use (e.g. 'spring_layout').
        max_vertices: Maximum number of vertices to include.
        output_file: If provided, the Plotly figure is saved to this file; otherwise it is displayed.
    """
    # Convert to a networkx graph
    G_nx = to_networkx(graph, max_vertices)

    # Compute positions using the given layout algorithm
    pos = getattr(nx, layout)(G_nx)

    # Extract node information: positions, labels, and colours based on their kind.
    x_values = [pos[node][0] for node in G_nx.nodes]
    y_values = [pos[node][1] for node in G_nx.nodes]
    labels = list(G_nx.nodes)
    # Use ACTOR_COLOR for 'actor' and MOVIE_COLOR for 'movie'
    colours = [ACTOR_COLOR if G_nx.nodes[node].get('kind') == 'actor' else MOVIE_COLOR
               for node in G_nx.nodes]

    # Prepare edge coordinates for Plotly
    x_edges = []
    y_edges = []
    for edge in G_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    # Create a scatter trace for edges
    edge_trace = Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        name='edges',
        line=dict(color=LINE_COLOR, width=3),
        hoverinfo='none'
    )

    # Create a scatter trace for nodes
    node_trace = Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        name='nodes',
        marker=dict(
            symbol='circle',
            size=20,
            color=colours,
            line=dict(color=VERTEX_BORDER_COLOR, width=3)
        ),
        text=labels,
        hovertemplate='%{text}',
        hoverlabel={'namelength': 0}
    )

    # Create the figure and update layout settings
    fig = Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False,
                      xaxis=dict(showgrid=False, zeroline=False, visible=False),
                      yaxis=dict(showgrid=False, zeroline=False, visible=False))

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)
