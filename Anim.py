import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
from database import IoTNodeData, get_available_nodes
import json
import socket
from typing import List

def init_graph():
    ax.clear()
    refresh_nodes()
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue',
            font_size=10, font_weight='bold', edge_color='gray', ax=ax)
    draw_battery_labels()
    ax.set_title("Initial IoT Network")
    plt.pause(0.1)

def update_ani(port):
    refresh_nodes()

    total_pheromone = sum(node.P_record[-1] for node in nodes)
    node_colors = []

    target_node = port_to_node.get(port)
    if not target_node:
        print(f"No device found for port {port}")
        return

    ax.clear()

    node_colors.append(1)
    for node in nodes:
        color = node.P_record[-1] / total_pheromone
        node_colors.append(color)

    nx.draw(G, pos, with_labels=True, node_size=2000, node_color= node_colors,
            font_size=10, font_weight='bold', edge_color='gray', ax=ax, cmap=plt.cm.plasma)

    nx.draw_networkx_edges(G, pos, edgelist=[('Host', target_node)],
                           edge_color='red', width=3, ax=ax)
    draw_battery_labels()
    ax.set_title(f"Task assigned to {target_node} (port {port})")
    plt.pause(0.001)

def refresh_nodes():
    global nodes, port_to_node
    nodes = get_available_nodes()
    port_to_node = {node.port: node.name for node in nodes}

def draw_battery_labels():
    for node in nodes:
        x, y = pos[node.name]
        battery = node.SoC_record[-1]
        ax.text(x, y - 0.4, f"{battery:.1f}%", fontsize=13, ha='center', color='black')

nodes : List[IoTNodeData] = []
for node in get_available_nodes():
    nodes.append(node)

port_to_node = {node.port: node.name for node in nodes}

G = nx.Graph()
G.add_node("Host", pos=(0, 0))

num_devices = 5
radius = 3
angle_step = 2 * np.pi / num_devices

for i, node in enumerate(nodes):
    angle = i * angle_step
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    G.add_node(node.name, pos=(x, y))
    G.add_edge("Host", node.name)

pos = nx.get_node_attributes(G, 'pos')

fig, ax = plt.subplots(figsize=(10, 8))

if __name__ == "__main__":
    init_graph()
    plt.show()
