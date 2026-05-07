"""
sjf.py
Member: Hazem
Responsibility: SJF Non-Preemptive Scheduling Algorithm (pure logic, no GUI)
"""


def run_sjf(processes: list) -> tuple:
    """
    Shortest Job First — Non-Preemptive.

    Once a process starts, it runs to completion without interruption.
    At each scheduling point, the available process with the smallest
    burst time is selected. Tie-breaking order:
        1. Smallest burst time
        2. Smallest arrival time
        3. Smallest process id (lexicographic)

    Parameters
    ----------
    processes : list of dicts  [{'id': 'P1', 'at': 0, 'bt': 6}, ...]

    Returns
    -------
    results        : list of dicts
                     [{'id', 'at', 'bt', 'ct', 'tat', 'wt', 'rt'}, ...]
    gantt_segments : list of tuples  [(process_id, start_time, end_time), ...]
    """

    # Work on a copy so we don't mutate the caller's list
    pool = list(processes)
    # Keep original order for building the results list at the end
    original_order = {p["id"]: p for p in processes}

    time           = 0
    gantt_segments = []
    completion_time = {}
    first_start     = {}
    done            = []          # ids in execution order

    while len(done) < len(pool):

        # All processes that have arrived and are not yet finished
        available = [p for p in pool
                     if p["at"] <= time and p["id"] not in done]

        if not available:
            # CPU is idle — jump to the next process arrival
            next_at = min(p["at"] for p in pool if p["id"] not in done)
            time    = next_at
            continue

        # Pick the shortest job; ties broken by AT, then by ID
        chosen = min(available,
                     key=lambda p: (p["bt"], p["at"], p["id"]))

        first_start[chosen["id"]]     = time
        completion_time[chosen["id"]] = time + chosen["bt"]

        gantt_segments.append((chosen["id"], time, time + chosen["bt"]))

        time += chosen["bt"]
        done.append(chosen["id"])

    # Build results list (in original arrival order)
    procs_sorted = sorted(processes, key=lambda p: (p["at"], p["id"]))
    results = []
    for p in procs_sorted:
        pid = p["id"]
        ct  = completion_time[pid]
        tat = ct - p["at"]
        wt  = tat - p["bt"]
        rt  = first_start[pid] - p["at"]
        results.append({
            "id":  pid,
            "at":  p["at"],
            "bt":  p["bt"],
            "ct":  ct,
            "tat": tat,
            "wt":  wt,
            "rt":  rt,
        })

    return results, gantt_segments
