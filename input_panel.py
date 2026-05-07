"""
input_panel.py
Member: Moaz
Responsibility: Input Panel & Validation
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------------------------------------------
#  SIMPLE STYLE CONSTANTS  (shared across all files)
# ---------------------------------------------------------------
BG       = "#f0f0f0"
WHITE    = "#ffffff"
BORDER   = "#aaaaaa"
TEXT     = "#111111"
SUBTEXT  = "#555555"
ACCENT   = "#336699"
BTN_ADD  = "#4a7c4e"
BTN_DEL  = "#8b2e2e"
BTN_CLR  = "#7a6a1e"
BTN_RUN  = "#1a5276"
FONT     = ("Arial", 10)
FONT_BOLD= ("Arial", 10, "bold")
FONT_SM  = ("Arial", 9)

# ---------------------------------------------------------------
#  PREDEFINED TEST SCENARIOS
# ---------------------------------------------------------------
SCENARIOS = [
    {
        "name":    "A - Basic Mixed Workload",
        "desc":    "Normal workload with varied burst times.",
        "procs":   [("P1",0,6),("P2",1,4),("P3",2,8),("P4",3,3),("P5",4,5)],
        "quantum": 3,
    },
    {
        "name":    "B - Short-Job-Heavy",
        "desc":    "Mostly short jobs. SJF efficiency is clearly visible.",
        "procs":   [("P1",0,2),("P2",0,1),("P3",1,3),("P4",1,1),("P5",2,2),("P6",2,1)],
        "quantum": 2,
    },
    {
        "name":    "C - Fairness Case",
        "desc":    "Equal burst times. RR distributes CPU time evenly.",
        "procs":   [("P1",0,8),("P2",0,8),("P3",0,8),("P4",0,8)],
        "quantum": 3,
    },
    {
        "name":    "D - Long-Job Sensitivity",
        "desc":    "One long process competes with short jobs.",
        "procs":   [("P1",0,20),("P2",1,2),("P3",2,3),("P4",3,1)],
        "quantum": 4,
    },
    {
        "name":    "E - Validation (Invalid Quantum)",
        "desc":    "Shows input validation: quantum = -1 is rejected.",
        "procs":   [("P1",0,5),("P2",1,3)],
        "quantum": -1,
    },
]


class InputPanel(tk.Frame):
    """
    Moaz's component.
    Provides all user input widgets: process table, quantum field,
    add/clear/run buttons, and full input validation.

    Public interface:
        get_process_data()  -> (list_of_dicts, tq_int) or None on error
        on_run              -> set this attribute to a callable(processes, tq)
                               that main.py will connect to the simulation.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.on_run = None          # main.py sets this callback

        self._build_quantum_section()
        self._build_process_table()
        self._build_action_buttons()
        self._build_scenarios_section()
        self._build_validation_label()
        self._build_run_button()

    # ----------------------------------------------------------------
    #  BUILD SECTIONS
    # ----------------------------------------------------------------
    def _build_quantum_section(self):
        qf = tk.LabelFrame(self, text="Time Quantum (Round Robin)",
                           bg=BG, fg=ACCENT, font=FONT_BOLD, padx=8, pady=6)
        qf.pack(fill="x", pady=(0, 8))

        row = tk.Frame(qf, bg=BG)
        row.pack(anchor="w")

        tk.Label(row, text="Quantum value:", bg=BG, fg=TEXT,
                 font=FONT).pack(side="left")

        self._q_var   = tk.StringVar(value="3")
        self._q_entry = tk.Entry(row, textvariable=self._q_var, width=7,
                                 font=FONT, bg=WHITE, fg=TEXT,
                                 insertbackground=TEXT, relief="solid", bd=1)
        self._q_entry.pack(side="left", padx=8)

        tk.Label(row, text="(positive integer only)", bg=BG, fg=SUBTEXT,
                 font=FONT_SM).pack(side="left")

    def _build_process_table(self):
        pf = tk.LabelFrame(self, text="Process Table",
                           bg=BG, fg=ACCENT, font=FONT_BOLD, padx=8, pady=6)
        pf.pack(fill="both", expand=True, pady=(0, 6))

        cols = ("PID", "Arrival Time", "Burst Time")
        self._proc_tree = ttk.Treeview(pf, columns=cols,
                                       show="headings", height=8)
        for c, w in zip(cols, [90, 120, 110]):
            self._proc_tree.heading(c, text=c)
            self._proc_tree.column(c, width=w, anchor="center", stretch=False)
        self._proc_tree.pack(fill="both", expand=True, pady=(0, 6))

        # Input row
        inp = tk.Frame(pf, bg=BG)
        inp.pack(fill="x", pady=(0, 6))
        self._entries = {}
        for lbl, key, w in [("PID", "pid", 7),
                             ("Arrival", "arrival", 8),
                             ("Burst", "burst", 8)]:
            tk.Label(inp, text=lbl + ":", bg=BG, fg=TEXT,
                     font=FONT).pack(side="left", padx=(4, 2))
            e = tk.Entry(inp, width=w, font=FONT, bg=WHITE, fg=TEXT,
                         insertbackground=TEXT, relief="solid", bd=1)
            e.pack(side="left", padx=(0, 8))
            e.bind("<Return>", lambda ev: self._add_process())
            self._entries[key] = e

    def _build_action_buttons(self):
        br = tk.Frame(self, bg=BG)
        br.pack(fill="x", pady=(0, 4))

        self._make_btn(br, "Add Process",
                       self._add_process, BTN_ADD).pack(side="left", padx=(0, 6))
        self._make_btn(br, "Remove Selected",
                       self._remove_process, BTN_DEL).pack(side="left", padx=(0, 6))
        self._make_btn(br, "Clear All",
                       self._clear_processes, BTN_CLR).pack(side="left")

    def _build_scenarios_section(self):
        sf = tk.LabelFrame(self, text="Test Scenarios",
                           bg=BG, fg=ACCENT, font=FONT_BOLD, padx=8, pady=6)
        sf.pack(fill="x", pady=(4, 4))

        # Use a horizontal layout to keep it compact
        grid = tk.Frame(sf, bg=BG)
        grid.pack(fill="x")

        for i, sc in enumerate(SCENARIOS):
            col = BTN_DEL if sc["quantum"] <= 0 else ACCENT
            btn_text = f"{sc['name'].split()[0]}  (Q={sc['quantum']})"
            self._make_btn(grid, btn_text,
                           lambda s=sc: self._load_scenario(s),
                           col, font_size=9,
                           pady=2).grid(row=i // 3, column=i % 3,
                                        padx=3, pady=2, sticky="w")

    def _build_validation_label(self):
        self._val_lbl = tk.Label(self, text="", bg=BG, fg="red",
                                 font=FONT_SM, wraplength=460, justify="left")
        self._val_lbl.pack(fill="x", pady=2)

    def _build_run_button(self):
        self._make_btn(self, "RUN SIMULATION",
                       self._on_run_clicked, BTN_RUN,
                       font_size=12, pady=8).pack(fill="x", pady=(4, 0))

    # ----------------------------------------------------------------
    #  PROCESS MANAGEMENT
    # ----------------------------------------------------------------
    def _add_process(self):
        try:
            pid     = self._entries["pid"].get().strip()
            arrival = self._entries["arrival"].get().strip()
            burst   = self._entries["burst"].get().strip()

            # --- validation ---
            if not pid:
                raise ValueError("PID cannot be empty.")

            existing = [self._proc_tree.item(i)["values"][0]
                        for i in self._proc_tree.get_children()]
            if pid in [str(e) for e in existing]:
                raise ValueError(f"PID '{pid}' already exists.")

            if not arrival.lstrip("-").isdigit():
                raise ValueError("Arrival Time must be a whole number.")
            if not burst.lstrip("-").isdigit():
                raise ValueError("Burst Time must be a whole number.")

            arr = int(arrival)
            bst = int(burst)

            if arr < 0:
                raise ValueError("Arrival Time must be >= 0.")
            if bst <= 0:
                raise ValueError("Burst Time must be > 0.")

            self._proc_tree.insert("", "end", values=(pid, arr, bst))
            for e in self._entries.values():
                e.delete(0, "end")
            self._val_lbl.config(text="")

        except ValueError as ex:
            self._val_lbl.config(text=f"Error: {ex}", fg="red")

    def _remove_process(self):
        for item in self._proc_tree.selection():
            self._proc_tree.delete(item)

    def _clear_processes(self):
        for item in self._proc_tree.get_children():
            self._proc_tree.delete(item)

    def _load_scenario(self, sc):
        self._clear_processes()
        for (pid, arr, burst) in sc["procs"]:
            self._proc_tree.insert("", "end", values=(pid, arr, burst))
        self._q_var.set(str(sc["quantum"]))
        self._val_lbl.config(
            text=f"Loaded scenario: {sc['name']}", fg="green")

    # ----------------------------------------------------------------
    #  VALIDATION & PUBLIC INTERFACE
    # ----------------------------------------------------------------
    def get_process_data(self):
        """
        Validates all inputs and returns (processes, tq) or None on error.
        processes = list of dicts: [{'id':'P1', 'at':0, 'bt':6}, ...]
        tq        = int (time quantum)
        """
        # --- validate quantum ---
        try:
            tq = int(self._q_var.get().strip())
            if tq <= 0:
                raise ValueError()
        except ValueError:
            msg = (
                f"Invalid Time Quantum: '{self._q_var.get()}'\n"
                "The quantum must be a positive integer (1, 2, 3, ...).\n"
                "Zero, negative values, and non-integers are not accepted."
            )
            self._val_lbl.config(text=msg, fg="red")
            messagebox.showerror(
                "Invalid Quantum",
                f"Quantum value '{self._q_var.get()}' is not valid.\n\n"
                "Rules:\n"
                "  - Must be a whole number\n"
                "  - Must be greater than 0\n\n"
                "Valid examples: 1, 2, 3, 4 ..."
            )
            return None

        # --- validate process count ---
        rows = self._proc_tree.get_children()
        if len(rows) < 2:
            self._val_lbl.config(
                text="Please add at least 2 processes before running.",
                fg="red")
            messagebox.showerror("Not Enough Processes",
                                 "Please add at least 2 processes.")
            return None

        # --- build process list ---
        processes = []
        for row in rows:
            v = self._proc_tree.item(row)["values"]
            processes.append({
                "id": str(v[0]),
                "at": int(v[1]),
                "bt": int(v[2]),
            })

        return processes, tq

    def _on_run_clicked(self):
        result = self.get_process_data()
        if result is None:
            return
        processes, tq = result
        self._val_lbl.config(
            text="Input valid. Simulation running...", fg="green")
        if callable(self.on_run):
            self.on_run(processes, tq)

    # ----------------------------------------------------------------
    #  HELPER
    # ----------------------------------------------------------------
    @staticmethod
    def _make_btn(parent, text, cmd, bg, fg="white",
                  font_size=10, **kw):
        return tk.Button(
            parent, text=text, command=cmd, bg=bg, fg=fg,
            activebackground=bg, activeforeground=fg,
            font=("Arial", font_size), relief="raised", bd=1,
            cursor="hand2", padx=8, **kw
        )
