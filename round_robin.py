def run_rr(processes, time_quantum):

    if not processes or time_quantum <= 0:
        return [], []

    # Make a local copy and add runtime fields
    procs = []
    for p in processes:
        procs.append({
            'id': p['id'],
            'at': p['at'],
            'bt': p['bt'],
            'rem': p['bt'],
            'first_run': -1,
            'ct': 0,
        })

    n = len(procs)
    time = 0
    completed = 0
    gantt = []
    ready = []
    in_queue = [False] * n
    i = 0

    procs.sort(key=lambda p: p['at'])

    while completed < n:
        while i < n and procs[i]['at'] <= time:
            ready.append(i)
            in_queue[i] = True
            i += 1

        if not ready:
            time = procs[i]['at']
            continue

        current = ready.pop(0)
        proc = procs[current]

        if proc['first_run'] == -1:
            proc['first_run'] = time

        run_time = min(proc['rem'], time_quantum)
        gantt.append((proc['id'], time, run_time))
        time += run_time
        proc['rem'] -= run_time

        while i < n and procs[i]['at'] <= time:
            ready.append(i)
            in_queue[i] = True
            i += 1

        if proc['rem'] == 0:
            proc['ct'] = time
            completed += 1
            in_queue[current] = False
        else:
            ready.append(current)

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