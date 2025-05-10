import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import json
import socket
from typing import List
import argparse
from database import IoTNodeData, get_available_nodes
# from Anim import update_ani
from architecture import render_iot_graph


def assign_task(instruction_count, alpha, beta, gamma, cum_turnaround_time):

    candidates : List[IoTNodeData] = []
    terminate = False
    for node in get_available_nodes():
        if node.SoC_record[-1] != 0:
            candidates.append(node)
        else:
            terminate = True
    if not candidates:
        print("No available nodes!")
        return -1
    if terminate:
        for node in candidates:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((node.ip, node.port))
                client.sendall(json.dumps({'type': 'TERMINATE'}).encode())
        print("Network died.")
        return -1

    # TTRC broadcast
    print('TTRC Broadcasting...')
    node_weights = []
    for node in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((node.ip, node.port))
            TTRC = json.dumps({
                'type': 'TTRC',
                'IC': instruction_count
            })
            client.sendall(TTRC.encode())
            TTRC_ACK = json.loads(client.recv(1024).decode())
            pheromone, ETT, SoC = TTRC_ACK['P_i,t(j)'], TTRC_ACK['ETT'], TTRC_ACK['SoC']
            node_weights.append((pheromone ** alpha) * (ETT ** (-beta)) * (SoC ** gamma))
    
    # Roulette Wheel Selection
    print('Roulette Wheel Selecting...')
    total_weights = sum(node_weights)
    probabilities = [nw / total_weights for nw in node_weights]
    selected_node = random.choices(candidates, probabilities)[0]
    print(f'Selection probability: {probabilities}')

    # Task Assignment
    print('Assigning Task...')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((selected_node.ip, selected_node.port))
        TA = json.dumps({
            'type': 'TA',
            'IC': instruction_count
        })
        client.sendall(TA.encode())
        TA_ACK = json.loads(client.recv(1024).decode())
        turnaround_time = TA_ACK['Exec Time']

    # here we make sure SoC and pheromone record has the same length for better comparison
    # this step is not required in real-world environment
    print('Wrapping Up...')
    for node in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            if node.port == selected_node.port:
                continue
            client.connect((node.ip, node.port))
            X = json.dumps({'type': 'X'})
            client.sendall(X.encode())
            _ = json.loads(client.recv(1024).decode())
    
    render_iot_graph(selected_node.port, cum_turnaround_time + turnaround_time)
    return turnaround_time


def vis_batteries_usage():
    plt.figure(figsize=(10, 5))
    for node in get_available_nodes():
        plt.plot(node.SoC_record, label=node.name)
    plt.xlabel("# of Tasks")
    plt.ylabel("Battery Percentage (%)")
    plt.title("Battery Drain for IoT Devices")
    plt.legend()
    plt.grid(True)
    plt.savefig("image/battery_drain.png", dpi=300, bbox_inches="tight")
    plt.close()

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="IoT Task Manager Simulation")
    parser.add_argument("--alpha", type=float, required=True, help="Pheromone Weight")
    parser.add_argument("--beta", type=float, required=True, help="ETT Weight")
    parser.add_argument("--gamma", type=float, required=True, help="SoC Weight")
    parser.add_argument("--max_iter", type=int, default=-1)

    args = parser.parse_args()
    alpha, beta, gamma = args.alpha, args.beta, args.gamma

    counter = 0
    task_queue = random.Random(42)
    res_time_record = []
    while True:
        nodes = get_available_nodes()
        print("\nRemaining Batteries and Pheromone:")
        for n in nodes:
            print(f"\t{n.name}: ({n.SoC_record[-1] * 100}%, {n.P_record[-1]})")
        print()
        res_time = assign_task(task_queue.randint(10, 100), alpha, beta, gamma, sum(res_time_record))
        vis_batteries_usage()
        if res_time < 0:
            break
        res_time_record.append(res_time)
        counter += 1
        if args.max_iter > 1 and counter >= args.max_iter:
            break

    print(f"# Tasks executed: {counter}")
    with open("data/turnaround_time/ctt.json", 'w') as f:
        json.dump({'response_time_record': res_time_record}, f, indent=4)
