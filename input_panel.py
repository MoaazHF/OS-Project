import tkinter as tk


process_entries = []


def create_header(frame):
    """Place column headers for the process table."""
    tk.Label(frame, text="ID", width=6).grid(row=0, column=1)
    tk.Label(frame, text="Arrival", width=6).grid(row=0, column=2)
    tk.Label(frame, text="Burst", width=6).grid(row=0, column=3)


def add_process_row(container, pid=None, at="0", bt="1"):
    """
    Add a new row of Entry widgets to `container`.
    If pid is None, auto‑assign based on current row count.
    """
    row = len(process_entries) + 1

    tk.Label(container, text=f"P{row}").grid(row=row, column=0, padx=5, pady=2)

    id_entry = tk.Entry(container, width=5)
    id_entry.grid(row=row, column=1, padx=5, pady=2)
    id_entry.insert(0, str(pid) if pid is not None else str(row))

    at_entry = tk.Entry(container, width=5)
    at_entry.grid(row=row, column=2, padx=5, pady=2)
    at_entry.insert(0, str(at))

    bt_entry = tk.Entry(container, width=5)
    bt_entry.grid(row=row, column=3, padx=5, pady=2)
    bt_entry.insert(0, str(bt))

    process_entries.append((id_entry, at_entry, bt_entry))
    return id_entry, at_entry, bt_entry


def remove_process_row():
    """Destroy the last row of Entry widgets and remove from list."""
    if process_entries:
        id_e, at_e, bt_e = process_entries.pop()
        id_e.destroy()
        at_e.destroy()
        bt_e.destroy()


def clear_all():
    """Remove all process rows."""
    while process_entries:
        remove_process_row()


def load_scenario(container, scenario, quantum_entry):

    clear_all()
    for p in scenario["processes"]:
        add_process_row(container, pid=p["id"], at=str(p["at"]), bt=str(p["bt"]))
    quantum_entry.delete(0, tk.END)
    quantum_entry.insert(0, str(scenario["quantum"]))


def get_processes_and_validate():

    processes = []
    errors = []
    for id_entry, at_entry, bt_entry in process_entries:
        try:
            pid = int(id_entry.get())
            at = int(at_entry.get())
            bt = int(bt_entry.get())
        except ValueError:
            errors.append("All fields must be integers.")
            continue
        if bt <= 0:
            errors.append(f"Process {pid}: Burst time must be > 0.")
        if at < 0:
            errors.append(f"Process {pid}: Arrival time cannot be negative.")
        processes.append({"id": pid, "at": at, "bt": bt})
    return processes, errors