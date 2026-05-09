import tkinter as tk
from tkinter import ttk
from round_robin import run_rr
from sjf import run_sjf
from gantt_chart import draw_gantt
from results_table import fill_results_table
from comparison import generate_comparison
import input_panel as inp

# ===================== PREDEFINED TEST SCENARIOS =====================
SCENARIOS = {
    "A": {
        "name": "Scenario A - Basic Mixed",
        "processes": [
            {"id": 1, "at": 0, "bt": 5},
            {"id": 2, "at": 1, "bt": 3},
            {"id": 3, "at": 2, "bt": 8},
            {"id": 4, "at": 3, "bt": 6},
        ],
        "quantum": 3
    },
    "B": {
        "name": "Scenario B - Short Job Heavy",
        "processes": [
            {"id": 1, "at": 0, "bt": 2},
            {"id": 2, "at": 1, "bt": 1},
            {"id": 3, "at": 2, "bt": 2},
            {"id": 4, "at": 3, "bt": 10},
        ],
        "quantum": 2
    },
    "C": {
        "name": "Scenario C - Fairness Case",
        "processes": [
            {"id": 1, "at": 0, "bt": 4},
            {"id": 2, "at": 0, "bt": 4},
            {"id": 3, "at": 0, "bt": 4},
            {"id": 4, "at": 0, "bt": 4},
        ],
        "quantum": 2
    },
    "D": {
        "name": "Scenario D - Long Job Sensitivity",
        "processes": [
            {"id": 1, "at": 0, "bt": 12},
            {"id": 2, "at": 1, "bt": 2},
            {"id": 3, "at": 2, "bt": 3},
            {"id": 4, "at": 3, "bt": 2},
        ],
        "quantum": 3
    },
    "E": {
        "name": "Scenario E - Validation (invalid)",
        "processes": [
            {"id": 1, "at": 0, "bt": 5},
            {"id": 2, "at": 1, "bt": -3},
        ],
        "quantum": 0
    }
}

# ===================== SIMULATION RUNNER =====================
def run_simulation():
    """Read inputs, run both algorithms, update all views."""
    try:
        quantum = int(quantum_entry.get())
    except ValueError:
        status_label.config(text="Error: Quantum must be an integer.")
        return
    if quantum <= 0:
        status_label.config(text="Error: Quantum must be > 0.")
        return

    processes, errors = inp.get_processes_and_validate()
    if errors:
        status_label.config(text="Validation failed: " + "; ".join(errors))
        return
    if not processes:
        status_label.config(text="Error: Add at least one process.")
        return

    rr_results, rr_gantt = run_rr(processes, quantum)
    sjf_results, sjf_gantt = run_sjf(processes)

    draw_gantt(canvas_rr, rr_gantt, "Round Robin Gantt Chart")
    draw_gantt(canvas_sjf, sjf_gantt, "SJF Gantt Chart")
    fill_results_table(rr_tree, rr_results)
    fill_results_table(sjf_tree, sjf_results)

    # Compute averages
    def avg(lst, key):
        return sum(p[key] for p in lst) / len(lst) if lst else 0

    rr_avg = {'avg_tat': avg(rr_results, 'tat'),
              'avg_wt': avg(rr_results, 'wt'),
              'avg_rt': avg(rr_results, 'rt')}
    sjf_avg = {'avg_tat': avg(sjf_results, 'tat'),
               'avg_wt': avg(sjf_results, 'wt'),
               'avg_rt': avg(sjf_results, 'rt')}

    comp_text = generate_comparison(rr_avg, sjf_avg, quantum)

    # Split into comparison summary and conclusion
    parts = comp_text.split("--- CONCLUSION ---")
    comparison_display.delete(1.0, tk.END)
    conclusion_display.delete(1.0, tk.END)
    if len(parts) == 2:
        comparison_display.insert(tk.END, parts[0].strip())
        conclusion_display.insert(tk.END, "--- CONCLUSION ---" + parts[1])
    else:
        comparison_display.insert(tk.END, comp_text)

    ready_list.delete(0, tk.END)
    for p in sorted(processes, key=lambda x: x['at']):
        ready_list.insert(tk.END, f"P{p['id']} (AT={p['at']})")

    status_label.config(text="Simulation completed successfully.")

# ===================== BUILD GUI =====================
root = tk.Tk()
root.title("OS Scheduler - Round Robin vs SJF")
root.geometry("1200x900")

main_canvas = tk.Canvas(root, borderwidth=0)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=main_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
main_canvas.configure(yscrollcommand=scrollbar.set)

main_frame = tk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
def on_frame_configure(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
main_frame.bind("<Configure>", on_frame_configure)

title_label = tk.Label(main_frame, text="Round Robin vs Shortest Job First",
                       font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# ===================== INPUT PANEL =====================
input_frame = tk.LabelFrame(main_frame, text="Process Input", padx=10, pady=10)
input_frame.pack(fill="x", padx=20, pady=5)

inp.create_header(input_frame)

process_container = tk.Frame(input_frame)
process_container.grid(row=1, column=0, columnspan=4, sticky="w")

btn_frame = tk.Frame(input_frame)
btn_frame.grid(row=2, column=0, columnspan=4, pady=5)
tk.Button(btn_frame, text="Add Process",
          command=lambda: inp.add_process_row(process_container)).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Remove Last",
          command=inp.remove_process_row).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Clear All",
          command=inp.clear_all).pack(side=tk.LEFT, padx=5)

quantum_frame = tk.Frame(input_frame)
quantum_frame.grid(row=3, column=0, columnspan=4, pady=5)
tk.Label(quantum_frame, text="Time Quantum:").pack(side=tk.LEFT)
quantum_entry = tk.Entry(quantum_frame, width=5)
quantum_entry.pack(side=tk.LEFT, padx=5)
quantum_entry.insert(0, "3")

# --- Scenario buttons ---
scenario_frame = tk.LabelFrame(main_frame, text="Test Scenarios", padx=10, pady=10)
scenario_frame.pack(fill="x", padx=20, pady=5)
for key in ["A", "B", "C", "D", "E"]:
    btn = tk.Button(scenario_frame, text=SCENARIOS[key]["name"],
                    command=lambda k=key: inp.load_scenario(process_container, SCENARIOS[k], quantum_entry))
    btn.pack(side=tk.LEFT, padx=5)

run_btn = tk.Button(main_frame, text="Run Simulation", font=("Arial", 12, "bold"),
                    command=run_simulation)
run_btn.pack(pady=10)

status_label = tk.Label(main_frame, text="Ready", fg="blue")
status_label.pack()

# ===================== GANTT CHARTS =====================
gantt_frame = tk.Frame(main_frame)
gantt_frame.pack(fill="x", padx=20, pady=5)

rr_gantt_label = tk.LabelFrame(gantt_frame, text="Round Robin", padx=5, pady=5)
rr_gantt_label.pack(side=tk.LEFT, fill="both", expand=True)
canvas_rr = tk.Canvas(rr_gantt_label, height=150, bg="white")
canvas_rr.pack(fill=tk.BOTH, expand=True)

sjf_gantt_label = tk.LabelFrame(gantt_frame, text="SJF", padx=5, pady=5)
sjf_gantt_label.pack(side=tk.RIGHT, fill="both", expand=True)
canvas_sjf = tk.Canvas(sjf_gantt_label, height=150, bg="white")
canvas_sjf.pack(fill=tk.BOTH, expand=True)

# ===================== RESULTS TABLES =====================
tables_frame = tk.Frame(main_frame)
tables_frame.pack(fill="x", padx=20, pady=5)

columns = ("ID", "AT", "BT", "CT", "TAT", "WT", "RT")

rr_table_frame = tk.LabelFrame(tables_frame, text="Round Robin Results", padx=5, pady=5)
rr_table_frame.pack(side=tk.LEFT, fill="both", expand=True)
rr_tree = ttk.Treeview(rr_table_frame, columns=columns, show="headings", height=6)
for col in columns:
    rr_tree.heading(col, text=col)
    rr_tree.column(col, width=50)
rr_tree.pack(fill=tk.BOTH, expand=True)

sjf_table_frame = tk.LabelFrame(tables_frame, text="SJF Results", padx=5, pady=5)
sjf_table_frame.pack(side=tk.RIGHT, fill="both", expand=True)
sjf_tree = ttk.Treeview(sjf_table_frame, columns=columns, show="headings", height=6)
for col in columns:
    sjf_tree.heading(col, text=col)
    sjf_tree.column(col, width=50)
sjf_tree.pack(fill=tk.BOTH, expand=True)

# ===================== READY QUEUE VIEW =====================
ready_frame = tk.LabelFrame(main_frame, text="Ready Queue (Arrival Order)", padx=5, pady=5)
ready_frame.pack(fill="x", padx=20, pady=5)
ready_list = tk.Listbox(ready_frame, height=3)
ready_list.pack(fill="x")

# ===================== COMPARISON & CONCLUSION =====================
comp_frame = tk.LabelFrame(main_frame, text="Comparison Summary", padx=5, pady=5)
comp_frame.pack(fill="x", padx=20, pady=5)
comparison_display = tk.Text(comp_frame, height=12, wrap=tk.WORD)
comparison_display.pack(fill="x")

conc_frame = tk.LabelFrame(main_frame, text="Conclusion", padx=5, pady=5)
conc_frame.pack(fill="x", padx=20, pady=5)
conclusion_display = tk.Text(conc_frame, height=10, wrap=tk.WORD)
conclusion_display.pack(fill="x")

# ===================== INITIAL SETUP =====================
for _ in range(4):
    inp.add_process_row(process_container)

main_frame.update_idletasks()
main_canvas.configure(scrollregion=main_canvas.bbox("all"))
root.mainloop()