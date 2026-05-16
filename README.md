# OS Scheduler Comparison: Round Robin vs SJF

GUI-based Operating Systems project to compare **Round Robin (RR)** and **Shortest Job First (SJF, non-preemptive)** using the same process workloads.

## Implemented Algorithms

### 1. Round Robin (`round_robin.py`)
- Preemptive time-sharing scheduler.
- Each ready process gets CPU for at most `q` time units, then rotates.
- Main strength: fairness and low response time for interactive workloads.
- Trade-off: may increase waiting/turnaround when quantum is poorly chosen.

### 2. Shortest Job First (`sjf.py`)
- Non-preemptive scheduler.
- At each dispatch point, selects the ready process with smallest burst time.
- Main strength: minimizes average waiting/turnaround in many batch workloads.
- Trade-off: long jobs can wait much longer (convoy/starvation tendency).

## Metrics Used
For each process:
- `CT` Completion Time
- `TAT = CT - AT` Turnaround Time
- `WT = TAT - BT` Waiting Time
- `RT = First_Run - AT` Response Time

Average values are compared across algorithms:
- Average Turnaround Time
- Average Waiting Time
- Average Response Time

Lower is better for all three metrics.

## How to Run

```bash
python3 main.py
```

Requirements:
- Python 3.x
- Tkinter (usually bundled with Python)

## Test Scenarios
Scenarios are defined in `main.py` and exposed in the GUI buttons.

| Scenario | Description | Processes (P: AT,BT) | Quantum |
|---|---|---|---|
| A | Basic Mixed | P1(0,5), P2(1,3), P3(2,8), P4(3,6) | 3 |
| B | Short Job Heavy | P1(0,2), P2(1,1), P3(2,2), P4(3,10) | 2 |
| C | Fairness Case | P1(0,4), P2(0,4), P3(0,4), P4(0,4) | 2 |
| D | Long Job Sensitivity | P1(0,12), P2(1,2), P3(2,3), P4(3,2) | 3 |
| E | Validation (Invalid Input) | P1(0,5), P2(1,-3) | 0 |

## Benchmark Results (Matches Screenshot Scenarios)

### Scenario A - Basic Mixed (q = 3)
| Algorithm | Avg TAT | Avg WT | Avg RT |
|---|---:|---:|---:|
| Round Robin | 14.00 | 8.50 | 3.00 |
| SJF | 10.75 | 5.25 | 5.25 |

Winner:
- Turnaround: **SJF**
- Waiting: **SJF**
- Response: **RR**

### Scenario B - Short Job Heavy (q = 2)
| Algorithm | Avg TAT | Avg WT | Avg RT |
|---|---:|---:|---:|
| Round Robin | 4.75 | 1.00 | 1.00 |
| SJF | 4.75 | 1.00 | 1.00 |

Winner: **Tie** on all metrics.

### Scenario C - Fairness Case (q = 2)
| Algorithm | Avg TAT | Avg WT | Avg RT |
|---|---:|---:|---:|
| Round Robin | 13.00 | 9.00 | 3.00 |
| SJF | 10.00 | 6.00 | 6.00 |

Winner:
- Turnaround: **SJF**
- Waiting: **SJF**
- Response: **RR**

### Scenario D - Long Job Sensitivity (q = 3)
| Algorithm | Avg TAT | Avg WT | Avg RT |
|---|---:|---:|---:|
| Round Robin | 9.00 | 4.25 | 2.50 |
| SJF | 13.75 | 9.00 | 9.00 |

Winner:
- Turnaround: **RR**
- Waiting: **RR**
- Response: **RR**

### Scenario E - Validation (Invalid Input)
Expected behavior:
- Reject `q <= 0`
- Reject `BT <= 0`
- Reject `AT < 0`
- Show validation errors in status bar

This confirms input-guard logic in `input_panel.py` and `main.py` is active.

## Screenshot Evidence
- Scenario A: `Screenshots/Scenario-A  Basic Mixed/`
- Scenario B: `Screenshots/Scenario-B  Short Job Heavy/`
- Scenario C: `Screenshots/Scenario-C  Fairness Case/`
- Scenario D: `Screenshots/Scenario-D  Long Job Sensitivity/`
- Scenario E: `Screenshots/Scenario-E  Validation (invalid)/`

## Final Comparison
- SJF is better for **average waiting and turnaround** in mixed/equal-job batches (Scenarios A and C).
- RR is better for **response time** in most tested cases (A, C, D), and dominates when long-job sensitivity appears (D).
- With this project's workloads, the choice is workload-dependent:
  - Prefer **SJF** for throughput-oriented batch completion.
  - Prefer **RR** for fairness and responsiveness.

## Notes on Interpretation
- The simulator does not model context-switch overhead cost explicitly.
- SJF here is **non-preemptive**.
- RR behavior is sensitive to quantum size.
