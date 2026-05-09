def run_sjf(processes):

    if not processes:
        return [], []

    procs = []
    for p in processes:
        procs.append({
            'id': p['id'],
            'at': p['at'],
            'bt': p['bt'],
            'rem': p['bt'],
            'first_run': -1,
            'ct': 0,
            'done': False
        })

    time = 0
    completed = 0
    n = len(procs)
    gantt = []

    while completed < n:
        best_idx = -1
        best_bt = float('inf')
        for i, p in enumerate(procs):
            if p['done']:
                continue
            if p['at'] <= time and p['bt'] < best_bt:
                best_bt = p['bt']
                best_idx = i

        if best_idx == -1:
            next_time = min(p['at'] for p in procs if not p['done'])
            gantt.append(("Idle", time, next_time - time))
            time = next_time
            continue

        proc = procs[best_idx]

        if proc['first_run'] == -1:
            proc['first_run'] = time

        run_time = proc['bt']
        gantt.append((proc['id'], time, run_time))
        time += run_time
        proc['rem'] = 0
        proc['ct'] = time
        proc['done'] = True
        completed += 1

    results = []
    for p in procs:
        tat = p['ct'] - p['at']
        wt = tat - p['bt']
        rt = p['first_run'] - p['at']
        results.append({
            'id': p['id'],
            'at': p['at'],
            'bt': p['bt'],
            'ct': p['ct'],
            'tat': tat,
            'wt': wt,
            'rt': rt
        })

    results.sort(key=lambda p: p['id'])
    return results, gantt