"""Functions for diplaying the graph."""

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


def visualize_actor_path(graph, path: list[str], fallback_actors: tuple[str, str] = None,
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
    if not path:
        if fallback_actors is not None:
            path = list(fallback_actors)
        else:
            print("No path found and no fallback actors provided.")
            return

    # Create a new NetworkX graph to represent the actor path.
    G = nx.Graph()

    # Add nodes for each actor in the path.
    for actor in path:
        G.add_node(actor, kind='actor')

    # Only add edges if a path was actually found (i.e. if fallback actors are not used)
    if len(path) > 1 and graph.get_common_movies(path[0], path[1]):
        for i in range(len(path) - 1):
            actor1 = path[i]
            actor2 = path[i + 1]
            common_movies = graph.get_common_movies(actor1, actor2)
            movies_str = '<br>'.join(sorted(common_movies)) if common_movies else ''
            G.add_edge(actor1, actor2, movies=movies_str)

    # Compute node positions using the selected layout algorithm.
    pos = getattr(nx, layout)(G)

    # Extract node coordinates and labels.
    x_values = [pos[node][0] for node in G.nodes()]
    y_values = [pos[node][1] for node in G.nodes()]
    labels = list(G.nodes())

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
    for edge in G.edges():
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    # Create a scatter trace for edges.
    edge_trace = Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        name='edges',
        line=dict(color='rgb(210,210,210)', width=edge_width),
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
        textfont=dict(size=node_font_size),  # Dynamically scaled node label size
        marker=dict(
            symbol='circle',
            size=node_size,
            color=actor_color,
            line=dict(color='rgb(50,50,50)', width=1)
        ),
        hovertemplate='%{text}',
        hoverlabel={'namelength': 0}
    )

    # Create a scatter trace for edge labels.
    edge_label_x = []
    edge_label_y = []
    edge_labels = []
    for edge in G.edges(data=True):
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
        textfont=dict(size=edge_font_size),  # Dynamically scaled edge label size
        hoverinfo='none'
    )

    # Build the figure.
    fig = Figure(data=[edge_trace, node_trace, edge_label_trace])
    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            showgrid=False, zeroline=False, visible=False,
            range=[min_x - buffer_x, max_x + buffer_x]
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, visible=False,
            range=[min_y - buffer_y, max_y + buffer_y]
        )
    )

    # Display or save the figure.
    if output_file:
        fig.write_image(output_file)
    else:
        fig.show()
