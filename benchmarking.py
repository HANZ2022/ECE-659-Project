import multiprocessing
import time
import numpy as np


def dummy_task():
    A = np.random.rand(500, 500)
    B = np.random.rand(500, 500)
    return np.dot(A, B)

def worker_task(count):
    for _ in range(count):
        dummy_task()
    return

def exec_task(instruction_count, PC):
    base_count = instruction_count // PC
    remainder = instruction_count % PC
    task_counts = [base_count + 1 if i < remainder else base_count for i in range(PC)]
    start = time.time()
    with multiprocessing.Pool(processes=PC) as pool:
        pool.map(worker_task, task_counts)
    end = time.time()
    return end - start

# def get_ETT_map():
#     ETT_map = [0]
#     i = 1
#     print("Initializing ETT...")
#     while ETT_map[-1] <= 1:
#         ETT_map.append(exec_task(i, 1))
#         i += 1
#         print(ETT_map[-1])
#     return ETT_map

def ETT(instruction_count, PC):
    return (0.005804 * instruction_count + 0.095973) / PC


def b1():
    primes = []
    for num in range(10000):
        if num > 1:
            for i in range(2, int(num**0.5)+1):
                if num % i == 0:
                    break
            else:
                primes.append(num)
    return primes

def b2():
    A = np.random.rand(500, 500)
    B = np.random.rand(500, 500)
    return np.dot(A, B)

def b3():
    lst = np.random.rand(10**6)
    return sorted(lst)

def b4():
    inside = 0
    for _ in range(10000):
        x, y = np.random.rand(), np.random.rand()
        if x**2 + y**2 <= 1:
            inside += 1
    return inside

def b5():
    def fib(n):
        if n <= 1:
            return n
        return fib(n-1) + fib(n-2)
    return fib(20)


def get_P0(PC):
    benchmarking_programs = [b1, b2, b3, b4, b5]
    N = len(benchmarking_programs)
    X = np.array([0.004, 0.008, 0.35, 0.02, 0.0006]) # pre-executed average
    Y = []
    for bp in benchmarking_programs:
        start = time.time()
        _ = bp()
        Y.append(time.time() - start)
    Y = np.array(Y)

    K_alpha = (
        (N * np.sum(X * Y) - np.sum(X) * np.sum(Y))
        /
        (N * np.sum(X ** 2) - (np.sum(X) ** 2))
    )
    T_benchmark = np.sum(Y)
    return (K_alpha * PC) / T_benchmark
