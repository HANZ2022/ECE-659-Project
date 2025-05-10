import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from database import IoTNodeData, get_available_nodes
from typing import List, Dict

def battery_to_color(battery: float):
    if battery >= 50:
        # Green to Yellow: (0, 1, 0) → (1, 1, 0)
        ratio = (battery - 50) / 50
        r = 1 - ratio
        g = 1.0
    else:
        # Yellow to Red: (1, 1, 0) → (1, 0, 0)
        ratio = battery / 50
        r = 1.0
        g = ratio
    return (r, g, 0)


def draw_battery_labels(ax, pos, nodes):
    for node in nodes:
        x, y = pos[node.name]
        battery = node.SoC_record[-1]
        color = battery_to_color(battery * 100.0)
        ax.text(x, y - 0.5, f"{(battery * 100.00):.2f}%", fontsize=11, ha='center', color=color)

        width, height = 0.6, 0.1
        left = x - width / 2
        bottom = y + 0.5
        battery_rect = plt.Rectangle((left, bottom), width, height, linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(battery_rect)

        fill_width = width * battery
        fill_rect = plt.Rectangle((left, bottom), fill_width, height, linewidth=0, facecolor=color)
        ax.add_patch(fill_rect)


def render_iot_graph(port, cum_turnaround_time, save_path="image/architecture.png"):
    nodes: List[IoTNodeData] = get_available_nodes()
    port_to_node: Dict[int, str] = {node.port: node.name for node in nodes}
    
    G = nx.Graph()
    G.add_node("Host", pos=(0, 0))

    num_devices = len(nodes)
    radius = 3
    angle_step = 2 * np.pi / max(num_devices, 1)
    pos = {"Host": (0, 0)}

    for i, node in enumerate(nodes):
        angle = i * angle_step
        x, y = radius * np.cos(angle), radius * np.sin(angle)
        G.add_node(node.name, pos=(x, y))
        G.add_edge("Host", node.name)
        pos[node.name] = (x, y)

    fig, ax = plt.subplots(figsize=(10, 8))

    if port is None:
        node_colors = ['skyblue'] + ['red'] * num_devices
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color=node_colors,
                font_size=10, font_weight='bold', edge_color='gray', ax=ax)
        ax.set_title("Initial IoT Network")
    else:
        total_pheromone = sum(node.P_record[-1] for node in nodes)
        node_colors = [(0.0, 1.0, 1.0, 1.0)]

        for node in nodes:
            alpha = node.P_record[-1] / total_pheromone if total_pheromone > 0 else 0
            node_colors.append((1.0, 0.0, 0.0, alpha))

        target_node = port_to_node.get(port)
        if not target_node:
            print(f"No device found for port {port}")
            return

        nx.draw(G, pos, with_labels=True, node_size=2000, node_color=node_colors,
                font_size=10, font_weight='bold', edge_color='gray', ax=ax, cmap=plt.cm.plasma)

        nx.draw_networkx_edges(G, pos, edgelist=[('Host', target_node)],
                               edge_color='red', width=3, ax=ax)
        # ax.set_title(f"Task assigned to {target_node} (port {port})")

    draw_battery_labels(ax, pos, nodes)
    ax.text(0, -0.5, f"Cumulative Response\nTime (s): {cum_turnaround_time:.2f}", fontsize=11, ha='center', color='black')

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)