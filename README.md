# EBS-RTTB: Energy Balancing System for IoT Network Real-time Task Balancing

This is the simulation implementation of EBS-RTTB paper. All the experimental setups are identical to the setup introduced in paper's methodology section.
If there is any issue when running this simulation please send email and we will assist you.

## Install Dependencies

```bash
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Run EBS-RTTB

To run the simulation in EBS-RTTB mode, follow these steps:

1. (Important!!!) If you have the following files in this project, rename (if you want to keep the previous experimental results) or delete (if you want to discard the previous execution results) these files:
    data/experiment.json
    data/turnaround_time/ctt.json
    image/architecture.png
    image/battery_drain.png

2. 
In a new terminal, run
```bash
# set w2 to 50 (set to 0 if you want to have pi-RTTB)
$ python start_nodes.py --w2 50

# sample output. please wait for all 5 devices to be initialized before proceeding to the next step
[iPhone 13 Pro] Listening on 127.0.0.1:57413
[Galaxy S21] Listening on 127.0.0.1:57414
[Realme GT] Listening on 127.0.0.1:57416
[Rock Pi] Listening on 127.0.0.1:57417
[Echo Dot] Listening on 127.0.0.1:57418
```

then open a new terminal and run
```bash
# set gamma to 1 (set to 0 if you want to have pi-RTTB)
$ python start_task_manager.py --alpha 1 --beta 1 --gamma 1

# sample output
Remaining Batteries and Pheromone:
        iPhone 13 Pro: (100%, 15.718302254665096)
        Galaxy S21: (100%, 21.073533268073554)
        Realme GT: (100%, 21.059179495232446)
        Rock Pi: (100%, 15.734396750649738)
        Echo Dot: (100%, 10.559521417443033)

TTRC Broadcasting...
Roulette Wheel Selecting...
Selection probability: [0.16603373240975275, 0.2968019766062534, 0.2965998164797665, 0.16620373990778206, 0.07436073459644535]
Assigning Task...
Wrapping Up...
```

3. At this step your simulation is started. You now have the following experimental results:
    data/experiment.json - contains SoC and pheromone information for each node
    data/turnaround_time/ctt.json - contains turnaround times for an experiment
    image/architecture.png - the "animated" image that keep refreshing when running, contains the architecture information
    image/battery_drain.png - the "animated" line plot that keep refreshing when running, contains SoC curve of each device

4. You can use tools in exp-vis.ipynb to generate plots inside the paper.

## More Usage
```bash
$ python start_nodes.py -h
usage: start_nodes.py [-h] [--w1 W1] --w2 W2 [--acceleration ACCELERATION]

IoT Node Simulation with Optional Energy Balancing

options:
  -h, --help            show this help message and exit
  --w1 W1               Real-time Weight # omega_1 in paper, default to 1
  --w2 W2               Energy-efficiency Weight # omega_2 in paper, must be provided
  --acceleration ACCELERATION
                        Simulation Speed # default 100 to speed up battery drainage, if you set to 1 then the simulation will be very similar to the real IoT drainage speed (can be very slow)
```

```bash
$ python start_task_manager.py -h
usage: start_task_manager.py [-h] --alpha ALPHA --beta BETA --gamma GAMMA [--max_iter MAX_ITER]

IoT Task Manager Simulation

options:
  -h, --help           show this help message and exit
  --alpha ALPHA        Pheromone Weight # alpha in paper, you can just set to 1 or any value you preferred
  --beta BETA          ETT Weight # beta in paper, you can just set to 1 or any value you preferred
  --gamma GAMMA        SoC Weight # gamma in paper, 0 to disable it, 1 to enable SoC in selection, >2 to give SoC more selection weights
  --max_iter MAX_ITER # maximum tasks to execute, default is -1 which will execute until a node die
```

## File Details & More Information
Anim.py - discarded, ignore it
architecture.py - for rendering image/architecture.png
battery.py - implementation of linear Columb Counting SoC
benchmarking.py - compuute P0, ETT, and execute dummy tasks, includes 5 benchmarking programs
database.py - store IoT node data, use TinyDB
exp-vis.ipynb - some tools to generate experimental plots
start_nodes.py - start simulated IoT nodes
start_task_manager.py - start simulated task manager

You can uncomment the function below in benchmarking.py to get ETT linear regression data:
```python
def get_ETT_map():
    ETT_map = [0]
    i = 1
    print("Initializing ETT...")
    while ETT_map[-1] <= 1:
        ETT_map.append(exec_task(i, 1))
        i += 1
        print(ETT_map[-1])
    return ETT_map
```

You can also change node_config below in start_nodes.py to introduce more nodes in the network:
```python
# (name, PC, A, SoC, w1, w2, acceleration_factor)
nodes_config = [
    ("iPhone 13 Pro", 6, 0.469, 1, w1, w2, acc_fac),
    ("Galaxy S21", 8, 0.45, 1, w1, w2, acc_fac),
    ("Realme GT", 8, 0.444, 1, w1, w2, acc_fac),
    ("Rock Pi", 6, 0.48, 1, w1, w2, acc_fac),
    ("Echo Dot", 4, 0.278, 1, w1, w2, acc_fac),
]
```

We have provided you some pre-executed experimental results under data/ and image/, you can use those for visualization too.
