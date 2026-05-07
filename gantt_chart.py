"""
gantt_chart.py
Member: Hany
Responsibility: Gantt Charts & Ready Queue View (visual display components)
"""

import tkinter as tk
from tkinter import ttk
import math

# ---------------------------------------------------------------
#  COLOR PALETTE — one color per process (up to 15)
# ---------------------------------------------------------------
PROC_COLORS = [
    "#5b9bd5", "#ed7d31", "#70ad47", "#ffc000", "#cc0000",
    "#4472c4", "#57a055", "#ff7f7f", "#9dc3e6", "#f4b942",
    "#7030a0", "#00b0f0", "#c00000", "#92d050", "#ff6600",
]

BG      = "#f0f0f0"
WHITE   = "#ffffff"
BORDER  = "#aaaaaa"
SUBTEXT = "#555555"
FONT_SM = ("Arial", 9)
FONT    = ("Arial", 10)


def _build_color_map(segments):
    """Return {process_id: color} derived from the order of first appearance."""
    seen = []
    for (pid, _, _) in segments:
        if pid not in seen:
            seen.append(pid)
    return {pid: PROC_COLORS[i % len(PROC_COLORS)] for i, pid in enumerate(seen)}


# ---------------------------------------------------------------
#  GANTT CHART
# ---------------------------------------------------------------
class GanttChart(tk.Frame):
    """
    Hany's Gantt chart component.

    Usage:
        chart = GanttChart(parent)
        chart.pack(fill="x")
        chart.redraw(segments, total_time)   # call whenever data changes

    segments   : list of (process_id, start_time, end_time)
    total_time : int — the last end time (used for scaling)
    color_map  : optional dict {pid: hex_color}; auto-generated if not given
    """

    MIN_BAR_WIDTH = 10    # px — bars are never drawn narrower than this

    def __init__(self, parent, title="Gantt Chart", **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._title = title
        self._build_widgets()

    def _build_widgets(self):
        tk.Label(self, text=self._title, font=("Arial", 10, "bold"),
                 bg=BG, fg="#336699").pack(anchor="w", pady=(4, 2))

        # Canvas + horizontal scrollbar
        cv_frame = tk.Frame(self, bg=BG)
        cv_frame.pack(fill="x")

        self._canvas = tk.Canvas(cv_frame, bg=WHITE, height=80,
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
        h_sb = ttk.Scrollbar(cv_frame, orient="horizontal",
                             command=self._canvas.xview)
        self._canvas.configure(xscrollcommand=h_sb.set)
        self._canvas.pack(fill="x", expand=True)
        h_sb.pack(fill="x")

        # Legend strip below the canvas
        self._legend = tk.Frame(self, bg=BG)
        self._legend.pack(anchor="w", padx=4, pady=(2, 4))

        self._placeholder()

    def _placeholder(self):
        self._canvas.delete("all")
        self._canvas.create_text(
            400, 40, text="No data — run the simulation first.",
            fill=SUBTEXT, font=FONT
        )

    # ------------------------------------------------------------------
    def redraw(self, segments, total_time, color_map=None):
        """Re-draw the Gantt chart with new data."""
        self._canvas.delete("all")
        for w in self._legend.winfo_children():
            w.destroy()

        if not segments:
            self._placeholder()
            return

        if color_map is None:
            color_map = _build_color_map(segments)

        # Determine pixel scale
        CANVAS_W = max(860, total_time * 30 + 60)
        BAR_H    = 34
        TOP      = 8
        BOT      = 26     # room for time labels
        H        = TOP + BAR_H + BOT + 6
        ML       = 6      # left margin

        scale = max(self.MIN_BAR_WIDTH,
                    min(32, int((CANVAS_W - ML * 2) / max(total_time, 1))))

        self._canvas.configure(
            height=H,
            scrollregion=(0, 0, ML * 2 + total_time * scale, H)
        )

        # Draw bars
        for (pid, s, e) in segments:
            x1 = ML + s * scale
            x2 = ML + e * scale
            # Enforce minimum visible width
            if x2 - x1 < self.MIN_BAR_WIDTH:
                x2 = x1 + self.MIN_BAR_WIDTH

            y1 = TOP
            y2 = TOP + BAR_H
            col = color_map.get(pid, "#5b9bd5")

            self._canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=col, outline=WHITE, width=1
            )
            if x2 - x1 > 10:
                self._canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=pid, fill="white",
                    font=("Arial", 8, "bold")
                )

        # Time tick marks and labels
        tick_step = max(1, math.ceil(total_time / 30))
        ticks = sorted(set(range(0, total_time + 1, tick_step)) | {0, total_time})
        for t in ticks:
            x = ML + t * scale
            self._canvas.create_line(
                x, TOP + BAR_H, x, TOP + BAR_H + 5,
                fill=SUBTEXT
            )
            self._canvas.create_text(
                x, TOP + BAR_H + 15,
                text=str(t), fill=SUBTEXT,
                font=("Courier", 8)
            )

        # Legend
        tk.Label(self._legend, text="Legend: ", bg=BG, fg=SUBTEXT,
                 font=FONT_SM).pack(side="left")
        seen = []
        for pid, _, _ in segments:
            if pid not in seen:
                seen.append(pid)
                col = color_map.get(pid, "#5b9bd5")
                tk.Label(self._legend,
                         text=f" {pid} ", bg=col, fg="white",
                         font=FONT_SM, relief="flat",
                         padx=3, pady=1).pack(side="left", padx=2)


# Convenience function (alternative to the class)
def draw_gantt(parent, segments, total_time, title="Gantt Chart", color_map=None):
    """
    Creates and packs a GanttChart directly into parent.
    Returns the GanttChart widget.
    """
    chart = GanttChart(parent, title=title)
    chart.pack(fill="x", pady=(0, 6))
    if segments:
        chart.redraw(segments, total_time, color_map)
    return chart


# ---------------------------------------------------------------
#  READY QUEUE VIEW  (Round Robin only)
# ---------------------------------------------------------------
class QueueView(tk.Frame):
    """
    Hany's Queue View component.

    Displays a scrollable log of ready-queue snapshots.
    Each line is one entry from queue_log (strings like
    't=0: Queue = [P2, P3]').

    Usage:
        qv = QueueView(parent)
        qv.pack(fill="both")
        qv.update(queue_log)    # list of strings
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._build_widgets()

    def _build_widgets(self):
        tk.Label(self, text="Ready Queue — Snapshots per Time Slice",
                 font=("Arial", 10, "bold"), bg=BG,
                 fg="#336699").pack(anchor="w", pady=(4, 2))

        text_frame = tk.Frame(self, bg=BG)
        text_frame.pack(fill="both", expand=True)

        self._text = tk.Text(
            text_frame,
            font=("Courier", 10),
            bg=WHITE, fg="#111111",
            relief="solid", bd=1,
            state="disabled",
            height=10,
            wrap="none",
        )
        sb_y = ttk.Scrollbar(text_frame, orient="vertical",
                             command=self._text.yview)
        sb_x = ttk.Scrollbar(text_frame, orient="horizontal",
                             command=self._text.xview)
        self._text.configure(yscrollcommand=sb_y.set,
                             xscrollcommand=sb_x.set)

        self._text.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")

        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self._placeholder_text()

    def _placeholder_text(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.insert("end", "No data — run the simulation first.")
        self._text.configure(state="disabled")

    def update(self, queue_log: list):
        """Refresh the view with a new list of queue snapshot strings."""
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")

        if not queue_log:
            self._text.insert("end", "(No snapshots recorded.)")
        else:
            for line in queue_log:
                self._text.insert("end", line + "\n")

        self._text.configure(state="disabled")
        self._text.see("1.0")
