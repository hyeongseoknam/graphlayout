import math
import random

def force_directed_layout(graph, iterations=50, k=0.1, c=0.01, p=0.1):
    """
    Computes the coordinates of nodes in a graph using the force-directed algorithm.

    Parameters:
        - graph (dict): A dictionary representing the graph. The keys are the node IDs and the values are lists of
          the IDs of the nodes that the key node is connected to.
        - iterations (int): The number of iterations to run the algorithm for.
        - k (float): The spring constant.
        - c (float): The damping factor.
        - p (float): The repulsion exponent.

    Returns:
        - A dictionary representing the layout of the graph. The keys are the node IDs and the values are tuples of
          the x and y coordinates of the node.
    """

    # Initialize the layout randomly.
    layout = {node_id: (random.random(), random.random()) for node_id in graph}

    # Run the algorithm for the specified number of iterations.
    for _ in range(iterations):
        # Compute the repulsive forces between nodes.
        repulsive_forces = {node_id: [0, 0] for node_id in graph}
        for node_id1 in graph:
            for node_id2 in graph:
                if node_id1 != node_id2:
                    x1, y1 = layout[node_id1]
                    x2, y2 = layout[node_id2]
                    dx, dy = x1 - x2, y1 - y2
                    d = max(math.sqrt(dx ** 2 + dy ** 2), 0.0001)
                    force = k ** p / d ** p
                    repulsive_forces[node_id1][0] += force * dx / d
                    repulsive_forces[node_id1][1] += force * dy / d

        # Compute the attractive forces between connected nodes.
        attractive_forces = {node_id: [0, 0] for node_id in graph}
        for node_id1, connections in graph.items():
            for node_id2 in connections:
                x1, y1 = layout[node_id1]
                x2, y2 = layout[node_id2]
                dx, dy = x1 - x2, y1 - y2
                d = max(math.sqrt(dx ** 2 + dy ** 2), 0.0001)
                force = d ** 2 / k
                attractive_forces[node_id1][0] -= force * dx / d
                attractive_forces[node_id1][1] -= force * dy / d
                attractive_forces[node_id2][0] += force * dx / d
                attractive_forces[node_id2][1] += force * dy / d

        # Compute the net forces on each node and update the layout.
        for node_id in graph:
            layout[node_id] = (
                (layout[node_id][0] + repulsive_forces[node_id][0] + attractive_forces[node_id][0]) * (1 - c),
                (layout[node_id][1] + repulsive_forces[node_id][1] + attractive_forces[node_id][1]) * (1 - c),
            )

    return layout
