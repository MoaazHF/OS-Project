"""
comparison.py
Member: Mohy
Responsibility: Comparison Panel, Conclusion Generator & Integration

Classes:
    ComparisonPanel  — side-by-side metrics table + winner highlight
                       + auto-generated conclusion display

Functions:
    generate_conclusion(rr_avg, sjf_avg, tq) -> str
"""

import tkinter as tk
from tkinter import ttk

# ── Shared style constants ───────────────────────────────────────────────────
BG         = "#f0f0f0"
WHITE      = "#ffffff"
ACCENT     = "#336699"
TEXT       = "#111111"
SUBTEXT    = "#555555"
WIN_COLOR  = "#c6efce"   # light green  — winning cell
LOSE_COLOR = "#ffc7ce"   # light red    — losing cell
TIE_COLOR  = "#ffeb9c"   # light yellow — tie cell
FONT       = ("Arial", 10)
FONT_BOLD  = ("Arial", 10, "bold")
FONT_TITLE = ("Arial", 13, "bold")
FONT_SM    = ("Arial", 9)


# ─────────────────────────────────────────────────────────────────────────────
#  generate_conclusion  (pure function — no GUI, easy to unit-test)
# ─────────────────────────────────────────────────────────────────────────────
def generate_conclusion(rr_avg: dict, sjf_avg: dict, tq: int) -> str:
    """
    Auto-generate a plain-text conclusion that answers all 6 analysis
    questions based on the averaged metrics.

    Parameters
    ----------
    rr_avg  : dict  {'avg_wt': float, 'avg_tat': float, 'avg_rt': float}
    sjf_avg : dict  {'avg_wt': float, 'avg_tat': float, 'avg_rt': float}
    tq      : int   time quantum used by Round Robin

    Returns
    -------
    str  — formatted multi-line conclusion text
    """

    def _winner(rr_val, sjf_val, metric_label):
        if rr_val < sjf_val:
            return f"Round Robin  ({metric_label}: RR={rr_val:.2f} < SJF={sjf_val:.2f})"
        elif sjf_val < rr_val:
            return f"SJF  ({metric_label}: SJF={sjf_val:.2f} < RR={rr_val:.2f})"
        else:
            return f"Tie  ({metric_label}: both = {rr_val:.2f})"

    # Q1 — average waiting time
    q1 = _winner(rr_avg["avg_wt"], sjf_avg["avg_wt"], "Avg WT")

    # Q2 — average response time
    q2 = _winner(rr_avg["avg_rt"], sjf_avg["avg_rt"], "Avg RT")

    # Q3 — fairness of RR
    q3 = (
        f"Yes. Round Robin rotates the CPU in fixed slices of Q={tq} units. "
        "Every process receives CPU access on a regular cycle regardless of "
        "its burst length, effectively preventing starvation."
    )

    # Q4 — SJF efficiency for short jobs
    q4 = (
        f"Yes. SJF always selects the shortest available job, minimising the "
        f"time shorter processes wait. "
        f"SJF Avg TAT = {sjf_avg['avg_tat']:.2f}  vs  "
        f"RR Avg TAT = {rr_avg['avg_tat']:.2f}."
    )

    # Q5 — quantum effect
    if tq <= 2:
        q5 = (
            f"Quantum = {tq} is small. This caused frequent context switches, "
            "keeping individual response times low but introducing higher "
            "scheduling overhead and potentially more total idle/switching cost."
        )
    elif tq <= 5:
        q5 = (
            f"Quantum = {tq} is moderate. It provided a good balance between "
            "CPU responsiveness and throughput, with a manageable number of "
            "context switches."
        )
    else:
        q5 = (
            f"Quantum = {tq} is large. Round Robin behaved similarly to FCFS: "
            "fewer context switches, but short jobs may have had to wait longer "
            "before their first CPU slice."
        )

    # Q6 — overall recommendation
    rr_wins  = sum([
        rr_avg["avg_wt"]  <= sjf_avg["avg_wt"],
        rr_avg["avg_tat"] <= sjf_avg["avg_tat"],
        rr_avg["avg_rt"]  <= sjf_avg["avg_rt"],
    ])
    if rr_wins >= 2:
        q6 = (
            "Round Robin is recommended for this workload. It achieved equal or "
            "lower metrics in at least 2 of the 3 measured categories, while "
            "also guaranteeing fairness and preventing starvation — making it "
            "the better choice for interactive or time-sharing systems."
        )
    else:
        q6 = (
            "SJF (Non-Preemptive) is recommended for this workload. It achieved "
            "lower average waiting and turnaround times by always prioritising "
            "the shortest available job. It is ideal for batch environments "
            "where burst times are known in advance and fairness is secondary."
        )

    # ── Format the full text ────────────────────────────────────────────────
    lines = [
        "=" * 72,
        "  ANALYSIS QUESTIONS & AUTO-GENERATED CONCLUSION",
        "=" * 72,
        "",
        "Q1. Which algorithm gave a lower average waiting time?",
        f"    {q1}",
        "",
        "Q2. Which algorithm gave a lower average response time?",
        f"    {q2}",
        "",
        "Q3. Did Round Robin appear fairer across all processes?",
        f"    {q3}",
        "",
        "Q4. Did SJF complete short jobs more efficiently?",
        f"    {q4}",
        "",
        f"Q5. How did the chosen quantum (Q={tq}) affect Round Robin?",
        f"    {q5}",
        "",
        "Q6. Which algorithm would you recommend for this workload?",
        f"    {q6}",
        "",
        "=" * 72,
        "  SUMMARY",
        "=" * 72,
        "",
        f"  Round Robin  — Avg WT: {rr_avg['avg_wt']:.2f} | "
        f"Avg TAT: {rr_avg['avg_tat']:.2f} | Avg RT: {rr_avg['avg_rt']:.2f}",
        f"  SJF          — Avg WT: {sjf_avg['avg_wt']:.2f} | "
        f"Avg TAT: {sjf_avg['avg_tat']:.2f} | Avg RT: {sjf_avg['avg_rt']:.2f}",
        "",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  ComparisonPanel  (tk.Frame)
# ─────────────────────────────────────────────────────────────────────────────
class ComparisonPanel(tk.Frame):
    """
    Mohy's Comparison Panel.

    Displays:
      1. A 3-row colour-coded metrics table (Avg WT / TAT / RT)
         — green = winner, red = loser, yellow = tie
      2. An overall "winner" label
      3. A scrollable text widget showing generate_conclusion() output

    Usage:
        panel = ComparisonPanel(parent)
        panel.pack(fill="both", expand=True)
        panel.update(rr_averages, sjf_averages, tq)

    rr_averages / sjf_averages must be dicts:
        {'avg_wt': float, 'avg_tat': float, 'avg_rt': float}
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build_widgets()

    # ── Build static skeleton ────────────────────────────────────────────────
    def _build_widgets(self):
        # Section title
        tk.Label(self, text="Side-by-Side Metrics Comparison",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 6))

        # ── Metrics comparison table (Canvas-based for cell colours) ─────────
        tbl_frame = tk.Frame(self, bg=BG)
        tbl_frame.pack(fill="x", pady=(0, 8))

        headers = ("Metric", "Round Robin", "SJF (Non-Preemptive)", "Winner")
        col_widths = (220, 130, 180, 90)

        # Header row
        for col, (hdr, w) in enumerate(zip(headers, col_widths)):
            tk.Label(tbl_frame, text=hdr, font=FONT_BOLD,
                     bg=ACCENT, fg=WHITE,
                     width=w // 8, anchor="center",
                     relief="flat", padx=4, pady=5
                     ).grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

        # Data rows (3 metrics)
        self._cells = []   # list of 4-tuples of Label widgets per row
        metric_names = [
            "Avg Waiting Time (WT)",
            "Avg Turnaround Time (TAT)",
            "Avg Response Time (RT)",
        ]
        for r, name in enumerate(metric_names, start=1):
            row_widgets = []
            for c in range(4):
                lbl = tk.Label(tbl_frame, text="—", font=FONT,
                               bg=WHITE, fg=TEXT,
                               width=col_widths[c] // 8,
                               anchor="center", relief="flat",
                               padx=4, pady=4)
                lbl.grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
                row_widgets.append(lbl)
            row_widgets[0].config(text=name, anchor="w")
            self._cells.append(tuple(row_widgets))

        # ── Overall winner label ─────────────────────────────────────────────
        self._winner_lbl = tk.Label(self, text="",
                                    font=("Arial", 11, "bold"),
                                    bg=BG, fg=ACCENT)
        self._winner_lbl.pack(anchor="w", pady=(0, 8))

        # ── Divider ──────────────────────────────────────────────────────────
        tk.Frame(self, height=1, bg="#aaaaaa").pack(fill="x", pady=4)

        # ── Conclusion text area ─────────────────────────────────────────────
        tk.Label(self, text="Analysis Questions & Conclusion",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 4))

        txt_frame = tk.Frame(self, bg=BG)
        txt_frame.pack(fill="both", expand=True)

        self._txt = tk.Text(
            txt_frame,
            font=("Courier", 10),
            bg=WHITE, fg=TEXT,
            relief="solid", bd=1,
            state="disabled",
            wrap="word",
            height=20,
        )
        sb_y = ttk.Scrollbar(txt_frame, orient="vertical",
                             command=self._txt.yview)
        self._txt.configure(yscrollcommand=sb_y.set)
        self._txt.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        txt_frame.rowconfigure(0, weight=1)
        txt_frame.columnconfigure(0, weight=1)

        self._show_placeholder()

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _show_placeholder(self):
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.insert("end", "Run the simulation first to see the conclusion.")
        self._txt.configure(state="disabled")

    def _set_text(self, text: str):
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.insert("end", text)
        self._txt.configure(state="disabled")
        self._txt.see("1.0")

    # ── Public update method ─────────────────────────────────────────────────
    def update(self, rr_avgs: dict, sjf_avgs: dict, tq: int):
        """
        Refresh the panel with fresh averaged metrics.

        Parameters
        ----------
        rr_avgs  : {'avg_wt': float, 'avg_tat': float, 'avg_rt': float}
        sjf_avgs : {'avg_wt': float, 'avg_tat': float, 'avg_rt': float}
        tq       : int  time quantum
        """
        keys = ["avg_wt", "avg_tat", "avg_rt"]

        rr_score  = 0
        sjf_score = 0

        for i, key in enumerate(keys):
            rr_val  = rr_avgs[key]
            sjf_val = sjf_avgs[key]

            rr_lbl, sjf_lbl, winner_lbl = (
                self._cells[i][1],
                self._cells[i][2],
                self._cells[i][3],
            )

            rr_lbl.config(text=f"{rr_val:.2f}")
            sjf_lbl.config(text=f"{sjf_val:.2f}")

            if rr_val < sjf_val:
                rr_lbl.config(bg=WIN_COLOR)
                sjf_lbl.config(bg=LOSE_COLOR)
                winner_lbl.config(text="RR", bg=WIN_COLOR, fg="#276221")
                rr_score += 1
            elif sjf_val < rr_val:
                sjf_lbl.config(bg=WIN_COLOR)
                rr_lbl.config(bg=LOSE_COLOR)
                winner_lbl.config(text="SJF", bg=WIN_COLOR, fg="#276221")
                sjf_score += 1
            else:
                rr_lbl.config(bg=TIE_COLOR)
                sjf_lbl.config(bg=TIE_COLOR)
                winner_lbl.config(text="Tie", bg=TIE_COLOR, fg="#7d6608")

        # Overall winner label
        if rr_score > sjf_score:
            winner_text = (
                f"★  Overall winner: Round Robin  "
                f"(better in {rr_score}/3 metrics)"
            )
            self._winner_lbl.config(text=winner_text, fg="#276221")
        elif sjf_score > rr_score:
            winner_text = (
                f"★  Overall winner: SJF (Non-Preemptive)  "
                f"(better in {sjf_score}/3 metrics)"
            )
            self._winner_lbl.config(text=winner_text, fg="#7b1818")
        else:
            self._winner_lbl.config(
                text="★  Overall result: Tie  (each algorithm leads in the same number of metrics)",
                fg="#7d6608"
            )

        # Fill the conclusion text widget
        conclusion_text = generate_conclusion(rr_avgs, sjf_avgs, tq)
        self._set_text(conclusion_text)
