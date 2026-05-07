"""
round_robin.py
Member: Hazem
Responsibility: Round Robin Scheduling Algorithm (pure logic, no GUI)
"""

from collections import deque


def run_rr(processes: list, tq: int) -> tuple:
    """
    Round Robin scheduling algorithm (preemptive, time-sliced).

    Parameters
    ----------
    processes : list of dicts  [{'id': 'P1', 'at': 0, 'bt': 6}, ...]
    tq        : int            Time Quantum (positive integer)

    Returns
    -------
    results        : list of dicts
                     [{'id', 'at', 'bt', 'ct', 'tat', 'wt', 'rt'}, ...]
    gantt_segments : list of tuples  [(process_id, start_time, end_time), ...]
    queue_log      : list of strings ['t=0: Queue = [P1, P2]', ...]
    """

    # Sort by arrival time; use id as secondary tie-break
    procs = sorted(processes, key=lambda p: (p["at"], p["id"]))
    n     = len(procs)

    # Working copies
    remaining_bt    = {p["id"]: p["bt"] for p in procs}
    first_start     = {}          # first time each process gets the CPU
    completion_time = {}

    ready_queue = deque()         # holds process ids
    gantt_segments = []
    queue_log      = []

    arrived = set()
    idx     = 0                   # pointer into sorted procs list
    time    = 0

    def enqueue_new_arrivals(up_to_time):
        """Add every process that has arrived by up_to_time to the queue."""
        nonlocal idx
        while idx < n and procs[idx]["at"] <= up_to_time:
            pid = procs[idx]["id"]
            if pid not in arrived:
                ready_queue.append(pid)
                arrived.add(pid)
            idx += 1

    # Seed the queue with processes that arrive at time 0
    enqueue_new_arrivals(time)

    while len(completion_time) < n:

        # If nothing is ready, the CPU is idle — jump forward to next arrival
        if not ready_queue:
            if idx < n:
                time = procs[idx]["at"]
                enqueue_new_arrivals(time)
            if not ready_queue:
                break                      # safety exit

        pid = ready_queue.popleft()

        # Log the queue state at this decision point
        queue_log.append(
            f"t={time}: Queue = [{', '.join(ready_queue)}]"
        )

        # Record first CPU access (for response time)
        if pid not in first_start:
            first_start[pid] = time

        # Execute for min(tq, remaining_bt)
        exec_slice = min(tq, remaining_bt[pid])
        start = time
        end   = time + exec_slice
        gantt_segments.append((pid, start, end))

        remaining_bt[pid] -= exec_slice
        time = end

        # Collect processes that arrived during this slice
        new_arrivals = []
        tmp = idx
        while tmp < n and procs[tmp]["at"] <= time:
            npid = procs[tmp]["id"]
            if npid not in arrived:
                new_arrivals.append(npid)
                arrived.add(npid)
            tmp += 1
        idx = tmp

        if remaining_bt[pid] == 0:
            # Process finished
            completion_time[pid] = time
            ready_queue.extend(new_arrivals)
        else:
            # Not done — put new arrivals first, then rotate this process back
            ready_queue.extend(new_arrivals)
            ready_queue.append(pid)

    # Build results list
    results = []
    for p in procs:
        pid = p["id"]
        ct  = completion_time.get(pid, time)
        tat = ct - p["at"]
        wt  = tat - p["bt"]
        rt  = first_start.get(pid, p["at"]) - p["at"]
        results.append({
            "id":  pid,
            "at":  p["at"],
            "bt":  p["bt"],
            "ct":  ct,
            "tat": tat,
            "wt":  wt,
            "rt":  rt,
        })

    return results, gantt_segments, queue_log
