def generate_comparison(rr_avg, sjf_avg, quantum):

    # Helper to pick the winner for each metric (lower is better)
    def winner(rr_val, sjf_val):
        if rr_val < sjf_val:
            return "Round Robin"
        elif sjf_val < rr_val:
            return "SJF"
        else:
            return "Tie"

    tat_winner = winner(rr_avg['avg_tat'], sjf_avg['avg_tat'])
    wt_winner  = winner(rr_avg['avg_wt'],  sjf_avg['avg_wt'])
    rt_winner  = winner(rr_avg['avg_rt'],  sjf_avg['avg_rt'])

    # Build the comparison block
    comparison = (
        "--- COMPARISON SUMMARY ---\n\n"

        f"Round Robin (Quantum = {quantum}):\n"
        f"  Average Turnaround Time : {rr_avg['avg_tat']:.2f}\n"
        f"  Average Waiting Time    : {rr_avg['avg_wt']:.2f}\n"
        f"  Average Response Time   : {rr_avg['avg_rt']:.2f}\n\n"

        f"SJF (Non‑Preemptive):\n"
        f"  Average Turnaround Time : {sjf_avg['avg_tat']:.2f}\n"
        f"  Average Waiting Time    : {sjf_avg['avg_wt']:.2f}\n"
        f"  Average Response Time   : {sjf_avg['avg_rt']:.2f}\n\n"

        "--- METRIC WINNERS ---\n\n"
        f"Turnaround Time : {tat_winner}\n"
        f"Waiting Time    : {wt_winner}\n"
        f"Response Time   : {rt_winner}\n\n"
    )

    # Auto‑generated conclusion answering the required questions
    conclusion = "--- CONCLUSION ---\n\n"

    # 1. Which algorithm gave lower average waiting time?
    conclusion += (
        f"1. Lower average waiting time: {wt_winner} "
        f"({rr_avg['avg_wt']:.2f} vs {sjf_avg['avg_wt']:.2f}).\n"
    )

    # 2. Which algorithm gave lower average response time?
    conclusion += (
        f"2. Lower average response time: {rt_winner} "
        f"({rr_avg['avg_rt']:.2f} vs {sjf_avg['avg_rt']:.2f}).\n"
    )

    # 3. Did Round Robin appear fairer across all processes?
    conclusion += (
        "3. Fairness: Round Robin generally distributes CPU time more evenly "
        "because every process receives frequent, regular time slices. "
        "Long processes cannot monopolise the CPU, and short processes do not starve. "
        "The continuous rotation prevents extreme individual waiting times.\n"
    )

    # 4. Did SJF complete short jobs more efficiently?
    conclusion += (
        "4. SJF completes short jobs more efficiently by immediately selecting "
        "the process with the smallest burst time. This minimises the convoy effect "
        "and reduces average waiting time, but at the cost of neglecting longer processes.\n"
    )

    # 5. How did the chosen quantum affect Round Robin behavior?
    conclusion += (
        f"5. Effect of quantum (q={quantum}): "
    )
    if quantum <= 2:
        conclusion += (
            "A very small quantum increases context‑switching overhead, "
            "which can artificially inflate turnaround times despite good response times. "
            "The system may behave almost like a time‑shared machine."
        )
    elif quantum <= 5:
        conclusion += (
            "A moderate quantum offers a balance between responsiveness and efficiency. "
            "Processes are not switched excessively, yet no process waits too long."
        )
    else:
        conclusion += (
            "A large quantum reduces the number of context switches, but Round Robin "
            "starts to behave more like First‑Come‑First‑Served, increasing response times "
            "for later processes and potentially hurting fairness."
        )
    conclusion += "\n"

    # 6. Recommendation for the tested workload
    conclusion += (
        "6. Recommendation: For this specific workload, "
    )
    if wt_winner == "SJF":
        conclusion += (
            "SJF achieved lower average waiting and turnaround times, making it more efficient "
            "for batch processing. However, if interactive responsiveness or fairness is critical, "
            "Round Robin remains the safer choice."
        )
    elif wt_winner == "Round Robin":
        conclusion += (
            "Round Robin performed better on waiting time, indicating that this workload "
            "benefits from time‑slicing. It also guarantees fairness, making it suitable "
            "for time‑sharing environments."
        )
    else:
        conclusion += (
            "both algorithms performed equally on the key metric, so the choice depends on "
            "whether you prioritise fairness (Round Robin) or pure efficiency (SJF)."
        )

    return comparison + conclusion