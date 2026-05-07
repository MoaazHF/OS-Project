"""
main.py
Member: Mohy (integration) + all team members
Responsibility: Application entry point — wires all modules together.

Team:
    Moaz  -> input_panel.py   (InputPanel)
    Hazem -> round_robin.py   (run_rr)
    Hazem -> sjf.py           (run_sjf)
    Hany  -> gantt_chart.py   (GanttChart, QueueView)
    Ahmed -> results_table.py (ResultsTable)
    Mohy  -> comparison.py    (ComparisonPanel, generate_conclusion)
             main.py          (SchedulerApp — integration)
"""

import tkinter as tk
from tkinter import ttk, messagebox

# ── Team members' modules ────────────────────────────────────────────────────
from input_panel   import InputPanel
from round_robin   import run_rr
from sjf           import run_sjf
from gantt_chart   import GanttChart, QueueView
from results_table import ResultsTable
from comparison    import ComparisonPanel          # Mohy's module

# ── Shared style constants ───────────────────────────────────────────────────
BG         = "#f0f0f0"
WHITE      = "#ffffff"
ACCENT     = "#336699"
TEXT       = "#111111"
SUBTEXT    = "#555555"
FONT       = ("Arial", 10)
FONT_BOLD  = ("Arial", 10, "bold")
FONT_TITLE = ("Arial", 13, "bold")

PROC_COLORS = [
    "#5b9bd5", "#ed7d31", "#70ad47", "#ffc000", "#cc0000",
    "#4472c4", "#57a055", "#ff7f7f", "#9dc3e6", "#f4b942",
    "#7030a0", "#00b0f0", "#c00000", "#92d050", "#ff6600",
]


# ── Utility helpers ──────────────────────────────────────────────────────────
def build_color_map(process_list: list) -> dict:
    """Map each process id to a consistent colour."""
    return {p["id"]: PROC_COLORS[i % len(PROC_COLORS)]
            for i, p in enumerate(process_list)}


def scrollable(parent):
    """
    Create a vertically-scrollable frame inside *parent*.
    Returns (outer_frame, inner_frame).
    Content should be packed into inner_frame.
    """
    outer  = tk.Frame(parent, bg=BG)
    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    sb     = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner  = tk.Frame(canvas, bg=BG)

    inner.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=sb.set)

    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    # Mouse-wheel scrolling
    canvas.bind_all(
        "<MouseWheel>",
        lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    )
    return outer, inner


def sep(parent, pad: int = 6):
    """Draw a thin horizontal separator line."""
    tk.Frame(parent, height=1, bg="#aaaaaa").pack(fill="x", pady=pad)


# ════════════════════════════════════════════════════════════════════════════
#  SchedulerApp  — main application class
# ════════════════════════════════════════════════════════════════════════════
class SchedulerApp:
    """
    Mohy's integration class.
    Builds the root window, notebook tabs, and wires all team modules together.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_window()
        self._build_header()
        self._build_notebook()

    # ── Window setup ────────────────────────────────────────────────────────
    def _configure_window(self):
        self.root.title("CPU Scheduling Simulator — RR vs SJF")
        self.root.geometry("960x680")
        self.root.minsize(800, 580)
        self.root.configure(bg=BG)

        # Notebook tab styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG,     borderwidth=0)
        style.configure("TNotebook.Tab",    background="#c8d8e8", foreground=TEXT,
                        font=FONT_BOLD,     padding=(10, 4))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])

    # ── Header banner ────────────────────────────────────────────────────────
    def _build_header(self):
        h = tk.Frame(self.root, bg=ACCENT, height=44)
        h.pack(fill="x")
        h.pack_propagate(False)

        tk.Label(h, text="CPU Scheduling Simulator",
                 bg=ACCENT, fg=WHITE,
                 font=("Arial", 16, "bold")).pack(side="left", padx=16)
        tk.Label(h,
                 text="Round Robin  vs  Shortest Job First (Non-Preemptive)",
                 bg=ACCENT, fg="#c8dff0",
                 font=("Arial", 11)).pack(side="left")

    # ── Notebook with 4 tabs ─────────────────────────────────────────────────
    def _build_notebook(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=8)
        self._nb = nb

        # ── Tab 1: Input (Moaz) ──────────────────────────────────────────────
        input_tab = tk.Frame(nb, bg=BG)
        nb.add(input_tab, text="  Input & Setup  ")

        pw = tk.PanedWindow(input_tab, orient="horizontal",
                            bg=BG, sashwidth=5, relief="flat")
        pw.pack(fill="both", expand=True, padx=8, pady=8)

        left_frame  = tk.Frame(pw, bg=BG)
        right_frame = tk.Frame(pw, bg=BG)
        pw.add(left_frame,  minsize=480)
        pw.add(right_frame, minsize=260)

        # Moaz's InputPanel
        self._input_panel = InputPanel(left_frame)
        self._input_panel.pack(fill="both", expand=True)
        self._input_panel.on_run = self._on_simulation_run   # wire callback

       # Scenarios
        info_box = tk.LabelFrame(right_frame, text="Scenarios",
                                 bg=BG, fg=ACCENT, font=FONT_BOLD,
                                 padx=8, pady=6)
        info_box.pack(fill="both", expand=True)
        tips = (
            "Scenario A:  Basic mixed workload \n\n"
            "Scenario B:  Short-job-heavy case \n\n"
            "Scenario C:  Fairness case\n\n"
            "Scenario D:  Long-job sensitivity case \n\n"
            "Scenario E: Validation case\n"
        )
        tk.Label(info_box, text=tips, bg=BG, fg=SUBTEXT,
                 font=FONT, justify="left", anchor="nw").pack(anchor="nw")

        # ── Tab 2: Round Robin (Hazem algo + Hany visuals + Ahmed table) ─────
        rr_tab = tk.Frame(nb, bg=BG)
        nb.add(rr_tab, text="  Round Robin  ")
        self._rr_tab = rr_tab
        self._placeholder(rr_tab, "Run the simulation to see Round Robin results.")

        # ── Tab 3: SJF (Hazem algo + Hany visuals + Ahmed table) ─────────────
        sjf_tab = tk.Frame(nb, bg=BG)
        nb.add(sjf_tab, text="  SJF  ")
        self._sjf_tab = sjf_tab
        self._placeholder(sjf_tab, "Run the simulation to see SJF results.")

        # ── Tab 4: Comparison (Mohy) ─────────────────────────────────────────
        cmp_tab = tk.Frame(nb, bg=BG)
        nb.add(cmp_tab, text="  Comparison  ")
        self._cmp_tab = cmp_tab
        self._placeholder(cmp_tab, "Run the simulation to see the comparison.")

    def _placeholder(self, tab: tk.Frame, msg: str):
        tk.Label(tab, text=msg, bg=BG, fg=SUBTEXT, font=FONT).pack(pady=40)

    # ── Simulation callback ──────────────────────────────────────────────────
    def _on_simulation_run(self, processes: list, tq: int):
        """
        Connected to Moaz's InputPanel.on_run.
        Drives all team modules in sequence and refreshes every tab.
        """
        try:
            color_map = build_color_map(processes)

            # Hazem: run both algorithms
            rr_results, rr_gantt, rr_queue_log = run_rr(processes, tq)
            sjf_results, sjf_gantt             = run_sjf(processes)

            # Render each tab
            self._render_rr_tab(rr_results, rr_gantt, rr_queue_log,
                                color_map, tq)
            self._render_sjf_tab(sjf_results, sjf_gantt, color_map)
            self._render_comparison_tab(rr_results, sjf_results, tq)

            # Jump to Round Robin tab after a successful run
            self._nb.select(1)

        except Exception as exc:
            messagebox.showerror(
                "Simulation Error",
                f"An unexpected error occurred:\n\n{exc}"
            )

    # ── Render: Round Robin tab ──────────────────────────────────────────────
    def _render_rr_tab(self, results, gantt, queue_log, color_map, tq):
        for w in self._rr_tab.winfo_children():
            w.destroy()

        outer, inner = scrollable(self._rr_tab)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=12, pady=8)

        tk.Label(inner, text="Round Robin — Simulation Results",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(anchor="w")
        tk.Label(inner, text=f"Time Quantum (Q) = {tq}",
                 font=FONT, bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(0, 8))

        # Hany: ready-queue view
        qv = QueueView(inner)
        qv.pack(fill="x", pady=(0, 8))
        qv.update(queue_log)

        sep(inner)

        # Hany: Gantt chart
        total = gantt[-1][2] if gantt else 1
        gc = GanttChart(inner, title="Gantt Chart — Round Robin")
        gc.pack(fill="x", pady=(0, 8))
        gc.redraw(gantt, total, color_map)

        sep(inner)

        # Ahmed: results table
        rt = ResultsTable(inner, title="Per-Process Metrics — Round Robin")
        rt.pack(fill="x", pady=(0, 8))
        rt.update(results)

    # ── Render: SJF tab ─────────────────────────────────────────────────────
    def _render_sjf_tab(self, results, gantt, color_map):
        for w in self._sjf_tab.winfo_children():
            w.destroy()

        outer, inner = scrollable(self._sjf_tab)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=12, pady=8)

        tk.Label(inner, text="SJF — Simulation Results (Non-Preemptive)",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(anchor="w", pady=(0, 8))

        # Hany: Gantt chart
        total = gantt[-1][2] if gantt else 1
        gc = GanttChart(inner, title="Gantt Chart — SJF")
        gc.pack(fill="x", pady=(0, 8))
        gc.redraw(gantt, total, color_map)

        sep(inner)

        # Ahmed: results table
        rt = ResultsTable(inner, title="Per-Process Metrics — SJF")
        rt.pack(fill="x", pady=(0, 8))
        rt.update(results)

    # ── Render: Comparison tab (Mohy's ComparisonPanel) ─────────────────────
    def _render_comparison_tab(self, rr_results, sjf_results, tq):
        for w in self._cmp_tab.winfo_children():
            w.destroy()

        outer, inner = scrollable(self._cmp_tab)
        outer.pack(fill="both", expand=True)
        inner.configure(padx=12, pady=8)

        tk.Label(inner, text="Algorithm Comparison",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(anchor="w", pady=(0, 8))

        # Ahmed's ResultsTable provides get_averages() — reuse for averages only
        rr_table  = ResultsTable(inner, title="Round Robin — Full Results")
        rr_table.pack(fill="x", pady=(0, 6))
        rr_table.update(rr_results)

        sjf_table = ResultsTable(inner, title="SJF — Full Results")
        sjf_table.pack(fill="x", pady=(0, 6))
        sjf_table.update(sjf_results)

        sep(inner, 8)

        rr_avgs  = rr_table.get_averages()
        sjf_avgs = sjf_table.get_averages()

        # Mohy: ComparisonPanel — colour-coded table + conclusion
        cmp_panel = ComparisonPanel(inner)
        cmp_panel.pack(fill="both", expand=True, pady=(0, 12))
        cmp_panel.update(rr_avgs, sjf_avgs, tq)


# ════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    SchedulerApp(root)
    root.mainloop()
