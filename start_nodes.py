import socket
import time
import random
import multiprocessing
import json
import argparse
import numpy as np
from database import IoTNodeData, nodes_table
# from battery import IoTBattery
from battery import IoTBatteryLinear
from benchmarking import get_P0, ETT, exec_task


class IoTNode(IoTNodeData):

    # node initialization
    def __init__(self, name, PC, A, SoC_0=1, w1=1, w2=1, acceleration=1):
        super().__init__()
        self.name, self.PC = name, PC
        self.P0 = get_P0(self.PC)
        self.P_record = [self.P0]
        self.SoC_record = [SoC_0]

        self._battery = IoTBatteryLinear(SoC_0, A, acceleration_factor=acceleration)
        self._w1, self._w2 = w1, w2


    # compute P_t+1
    def update_pheromone(self, R_a, R_e):
        w1, w2 = self._w1, self._w2
        P_new = self.P0 / (
            w1 * max(R_a - R_e, 0) +
            w2 * (1 - self.SoC_record[-1]) + 1
        )
        self.P_record.append(P_new)


    def execute_task(self, IC):
        R_e = ETT(IC, self.PC)
        R_a = exec_task(IC, self.PC)
        self._battery.drain(R_a)
        self.SoC_record.append(self._battery.SoC)
        self.update_pheromone(R_a, R_e)
        return R_a
    

    def start_server(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.ip, 0))
            self.port = server.getsockname()[1]
            self.update_db()
            print(f"[{self.name}] Listening on {self.ip}:{self.port}")

            server.listen()
            terminate = False
            while not terminate:
                conn, _ = server.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
                    task_request = json.loads(data.decode())

                    # TTRC
                    if task_request['type'] == 'TTRC':
                        conn.sendall(json.dumps({
                            'P_i,t(j)': self.P_record[-1],
                            'ETT': ETT(task_request['IC'], self.PC),
                            'SoC': self.SoC_record[-1]
                        }).encode())

                    # Task Assignment
                    if task_request['type'] == 'TA':
                        exec_time = self.execute_task(task_request['IC'])
                        self.update_db()
                        conn.sendall(json.dumps({'Exec Time': exec_time}).encode())
                    
                    # just ensure nodes have the same SoC and pheromone record length
                    if task_request['type'] == 'X':
                        self.SoC_record.append(self.SoC_record[-1])
                        self.P_record.append(self.P_record[-1])
                        self.update_db()
                        conn.sendall(json.dumps({'X': 'X'}).encode())

                    if task_request['type'] == 'TERMINATE':
                        terminate = True

                # node died
                if self._battery.SoC == 0:
                    print(f"[{self.name}] Battery Drained! Shutting down...")
                    break


def start_node(name, PC, A, SoC, w1, w2, acceleration):
    node = IoTNode(name, PC, A, SoC, w1, w2, acceleration)
    node.start_server()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IoT Node Simulation with Optional Energy Balancing")
    parser.add_argument("--w1", type=float, default=1.0, help="Real-time Weight")
    parser.add_argument("--w2", type=float, required=True, help="Energy-efficiency Weight")
    parser.add_argument("--acceleration", type=float, default=100.0, help="Simulation Speed")
    args = parser.parse_args()
    w1, w2, acc_fac = args.w1, args.w2, args.acceleration

    # (name, PC, A, SoC, w1, w2, acceleration_factor)
    nodes_config = [
        ("iPhone 13 Pro", 6, 0.469, 1, w1, w2, acc_fac),
        ("Galaxy S21", 8, 0.45, 1, w1, w2, acc_fac),
        ("Realme GT", 8, 0.444, 1, w1, w2, acc_fac),
        ("Rock Pi", 6, 0.48, 1, w1, w2, acc_fac),
        ("Echo Dot", 4, 0.278, 1, w1, w2, acc_fac),
    ]

    processes = []
    for node in nodes_config:
        p = multiprocessing.Process(target=start_node, args=node)
        p.start()
        processes.append(p)
        time.sleep(1)
    for p in processes:
        p.join()