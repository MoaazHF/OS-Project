"""
results_table.py
Member: Ahmed
Responsibility: Results Tables & Metrics Display
"""

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------
#  STYLE CONSTANTS
# ---------------------------------------------------------------
BG        = "#f0f0f0"
WHITE     = "#ffffff"
ROW_EVEN  = "#dce8f5"     # alternating row colour
ACCENT    = "#336699"
TEXT      = "#111111"
FONT      = ("Arial", 10)
FONT_BOLD = ("Arial", 10, "bold")


class ResultsTable(tk.Frame):
    """
    Ahmed's results table component.

    Displays per-process scheduling metrics in a styled Treeview,
    with alternating row colours and an 'Average' summary row at the bottom.

    Usage:
        table = ResultsTable(parent, title="Round Robin Results")
        table.pack(fill="x")
        table.update(results)       # pass list of result dicts
        avgs = table.get_averages() # {'avg_wt': x, 'avg_tat': y, 'avg_rt': z}

    results items must have keys: id, at, bt, ct, tat, wt, rt
    """

    COLUMNS = ("Process", "AT", "BT", "CT", "TAT", "WT", "RT")
    WIDTHS   = (80, 60, 60, 80, 70, 70, 70)

    def __init__(self, parent, title="Results Table", **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._title    = title
        self._averages = {}
        self._build_widgets()

    # ----------------------------------------------------------------
    #  BUILD
    # ----------------------------------------------------------------
    def _build_widgets(self):
        tk.Label(self, text=self._title, font=FONT_BOLD,
                 bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 2))

        tk.Frame(self, height=1, bg="#aaaaaa").pack(fill="x", pady=(0, 4))

        # Style
        style = ttk.Style()
        style.configure("Results.Treeview",
                        background=WHITE,
                        foreground=TEXT,
                        fieldbackground=WHITE,
                        rowheight=24,
                        font=FONT)
        style.configure("Results.Treeview.Heading",
                        background=ACCENT,
                        foreground="white",
                        font=FONT_BOLD)
        style.map("Results.Treeview",
                  background=[("selected", "#b8d4ea")],
                  foreground=[("selected", TEXT)])

        # Treeview + scrollbar
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="x")

        self._tree = ttk.Treeview(
            frame,
            columns=self.COLUMNS,
            show="headings",
            style="Results.Treeview",
            height=6,
        )

        for col, w in zip(self.COLUMNS, self.WIDTHS):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center", stretch=False)

        # Tag for alternating rows
        self._tree.tag_configure("even",    background=ROW_EVEN)
        self._tree.tag_configure("odd",     background=WHITE)
        # Tag for the average summary row
        self._tree.tag_configure("average",
                                 background=ACCENT,
                                 foreground="white",
                                 font=FONT_BOLD)

        sb = ttk.Scrollbar(frame, orient="vertical",
                           command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)

        self._tree.pack(side="left", fill="x", expand=True)
        sb.pack(side="left", fill="y")

        # Placeholder text shown before data is loaded
        self._placeholder_row()

    def _placeholder_row(self):
        self._tree.insert("", "end",
                          values=("—", "—", "—", "—", "—", "—",
                                  "Run simulation to see results"),
                          tags=("odd",))

    # ----------------------------------------------------------------
    #  PUBLIC METHODS
    # ----------------------------------------------------------------
    def update(self, results: list):
        """
        Refresh the table with a new results list.

        Each item in results must be a dict with keys:
            id, at, bt, ct, tat, wt, rt
        """
        # Clear existing rows
        for row in self._tree.get_children():
            self._tree.delete(row)

        if not results:
            self._placeholder_row()
            self._averages = {}
            return

        # Insert one row per process with alternating colours
        for i, m in enumerate(results):
            tag = "even" if i % 2 == 0 else "odd"
            self._tree.insert("", "end",
                              values=(m["id"], m["at"], m["bt"], m["ct"],
                                      m["tat"], m["wt"], m["rt"]),
                              tags=(tag,))

        # Compute averages
        n = len(results)
        avg_wt  = sum(m["wt"]  for m in results) / n
        avg_tat = sum(m["tat"] for m in results) / n
        avg_rt  = sum(m["rt"]  for m in results) / n
        self._averages = {
            "avg_wt":  avg_wt,
            "avg_tat": avg_tat,
            "avg_rt":  avg_rt,
        }

        # Average summary row at the bottom
        self._tree.insert("", "end",
                          values=("Average", "—", "—", "—",
                                  f"{avg_tat:.2f}",
                                  f"{avg_wt:.2f}",
                                  f"{avg_rt:.2f}"),
                          tags=("average",))

        # Resize treeview height to fit all rows + average row
        self._tree.configure(height=n + 1)

    def get_averages(self) -> dict:
        """
        Returns {'avg_wt': float, 'avg_tat': float, 'avg_rt': float}.
        Returns an empty dict if update() has not been called yet.
        """
        return dict(self._averages)
