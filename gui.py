#!/usr/bin/env python3
"""
gui.py - Tkinter GUI for the Connect 4 Minimax / Alpha-Beta agent.

Run with:      python gui.py

This file only IMPORTS the existing modules (board.py, alphabeta.py,
hurastic.py, tree.py) - none of them are modified.

What the GUI covers from the assignment sheet (Lab 2-A.pdf):
  * Human vs. computer, played until the board is full
  * K (the depth limit) is chosen before the game begins
  * Winner = the player with the greater number of connected-fours
  * The minimax tree of every AI turn is DRAWN as a real tree
    (triangles = MAX, inverted triangles = MIN, squares = leaves,
     red X = branch pruned by alpha-beta)
  * The heuristic values of the board are shown (click any node to see
    its board, the window counts and the value of H)
  * Time taken and nodes expanded per AI move (useful for the report)
"""

import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# the solver modules may live in ./src (harmless if they are next to gui.py)


from src.board import (
    initilize_board,
    legalmove,
    makemove,
    isboardfilled,
    ROWS,
    COL,
    AI,
    HUMAN,
)
from src.alphabeta import bestmove
from src.hurastic import get_all_windows, H, weight

# ----------------------------------------------------------------- look & feel
CELL = 80  # size of one cell on the main board (px)
PAD = 8  # gap between a disc and its cell border
HEADER = CELL  # empty strip above the board (hover / drop area)
BOARD_W = COL * CELL
BOARD_H = HEADER + ROWS * CELL

C_BOARD = "#2f5bea"
C_EMPTY = "#d9d9d9"
C_AI = "#d62828"  # red
C_HUMAN = "#f6c90e"  # yellow
C_OUTLINE = "#1b2f7a"

MINI_CELL = 32  # size of a cell in the small preview board

# drawn-tree geometry
LEVEL_H = 95  # vertical distance between tree levels
X_GAP = 56  # horizontal distance between leaf slots
R = 15  # node "radius"
TOP = 30
LEFT = 40
MAX_DRAWN = 4000  # never draw more nodes than this
C_MAX = "#bfd9ff"
C_MIN = "#ffd9bf"
C_LEAF = "#e3e3e3"
C_PV = "#1a9d3a"  # best line (green)
C_PRUNE = "#d32f2f"  # pruned (red)
ZOOM_MIN = 0.02  # smallest / largest tree zoom factor
ZOOM_MAX = 4.0
DEFAULT_ZOOM = 0.5  # zoom used when a new tree is drawn (50%)
ZOOM_STEP = 1.25  # factor used by the + / - buttons and Ctrl+wheel


# ------------------------------------------------------------------- helpers
def piece_color(value):
    if value == AI:
        return C_AI
    if value == HUMAN:
        return C_HUMAN
    return C_EMPTY


def fmt(v):
    """Pretty-print a minimax / heuristic value."""
    if v is None:
        return "-"
    v = float(v)
    if v == float("inf"):
        return "+inf"
    if v == float("-inf"):
        return "-inf"
    return f"{v:.1f}"


def draw_grid(canvas, board, cell, top=0, pad=PAD):
    """Draw the blue board with discs on any canvas."""
    canvas.create_rectangle(
        0, top, COL * cell, top + ROWS * cell, fill=C_BOARD, outline=C_OUTLINE, width=2
    )
    for r in range(ROWS):
        for c in range(COL):
            x0 = c * cell + pad
            y0 = top + r * cell + pad
            d = cell - 2 * pad
            canvas.create_oval(
                x0,
                y0,
                x0 + d,
                y0 + d,
                fill=piece_color(board[r][c]),
                outline=C_OUTLINE,
                width=2,
            )


def count_nodes(root):
    """Number of nodes in the minimax tree (nodes actually expanded)."""
    total, stack = 0, [root]
    while stack:
        n = stack.pop()
        total += 1
        stack.extend(n.children)
    return total


def count_levels(root, levels):
    """Number of nodes that would be drawn when showing `levels` levels."""
    total, stack = 0, [(root, 0)]
    while stack:
        n, lvl = stack.pop()
        total += 1
        if lvl < levels:
            stack.extend((ch, lvl + 1) for ch in n.children)
    return total


def tree_depth(root):
    return max(n.depth for n in _walk(root)) - root.depth


def _walk(root):
    stack = [root]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(n.children)


def is_max_node(n):
    """The root and nodes created by a HUMAN move are MAX (AI moves next)."""
    return n.player is None or n.player == HUMAN


# ----------------------------------------------------------------------- GUI
class Connect4GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect 4 - Minimax with Alpha-Beta Pruning")
        self.configure(padx=10, pady=10)
        self.resizable(True, True)

        self.board = initilize_board()
        self.k = 4
        self.game_on = False  # a game is in progress
        self.busy = True  # True while AI thinks / disc is falling
        self._result = None

        # tree-drawing state
        self.root_node = None  # full tree of the last AI move
        self.view_root = None  # sub-tree currently displayed
        self.selected = None
        self.pv_ids = set()
        self.tag_node = {}  # canvas tag -> Node
        self.node_pos = {}  # id(Node) -> (x, y)
        self._press = None
        self._zoom = 1.0  # current zoom of the drawn tree
        self._texts = []  # (canvas id, base font size, bold) for zooming labels
        self._base = (1, 1)  # unzoomed width / height of the drawn tree

        self._build_controls()
        self._build_board_area()
        self._build_tree_area()
        self.redraw()
        self.set_status("Choose K and press  Start Game.")

    # ------------------------------------------------------------ layout
    def _build_controls(self):
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Label(bar, text="K (search depth):").pack(side="left")
        self.k_var = tk.StringVar(value="4")
        ttk.Spinbox(bar, from_=1, to=12, width=4, textvariable=self.k_var).pack(
            side="left", padx=(4, 14)
        )

        ttk.Label(bar, text="First move:").pack(side="left")
        self.first_var = tk.StringVar(value="AI")
        ttk.Combobox(
            bar,
            width=7,
            state="readonly",
            textvariable=self.first_var,
            values=["AI", "Human"],
        ).pack(side="left", padx=(4, 14))

        ttk.Button(bar, text="Start Game", command=self.start_game).pack(side="left")

        # colour legend
        legend = tk.Canvas(bar, width=250, height=24, highlightthickness=0)
        legend.pack(side="right")
        legend.create_oval(2, 3, 20, 21, fill=C_AI, outline=C_OUTLINE)
        legend.create_text(26, 12, text="AI", anchor="w")
        legend.create_oval(70, 3, 88, 21, fill=C_HUMAN, outline=C_OUTLINE)
        legend.create_text(94, 12, text="You (Human)", anchor="w")

    def _build_board_area(self):
        left = ttk.Frame(self)
        left.grid(row=1, column=0, sticky="n")

        self.canvas = tk.Canvas(
            left,
            width=BOARD_W,
            height=BOARD_H,
            highlightthickness=0,
            bg=self.cget("bg"),
        )
        self.canvas.pack()
        self.canvas.bind("<Motion>", self.on_hover)
        self.canvas.bind("<Leave>", lambda e: self.canvas.delete("ghost"))
        self.canvas.bind("<Button-1>", self.on_click)

        # column numbers under the board
        nums = tk.Canvas(
            left, width=BOARD_W, height=22, highlightthickness=0, bg=self.cget("bg")
        )
        nums.pack()
        for c in range(COL):
            nums.create_text(c * CELL + CELL // 2, 11, text=str(c + 1))

        self.status = tk.StringVar()
        ttk.Label(
            left,
            textvariable=self.status,
            font=("Helvetica", 12, "bold"),
            wraplength=BOARD_W,
            justify="center",
        ).pack(pady=(8, 2))

        self.score_var = tk.StringVar()
        ttk.Label(
            left, textvariable=self.score_var, font=("Courier", 10), justify="left"
        ).pack(pady=(2, 0))

        self.stats_var = tk.StringVar(value="")
        ttk.Label(
            left,
            textvariable=self.stats_var,
            font=("Courier", 10),
            justify="left",
            foreground="#444",
        ).pack(pady=(6, 0))

    def _build_tree_area(self):
        right = ttk.LabelFrame(self, text=" Minimax tree of the last AI move ")
        right.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        ctl = ttk.Frame(right)
        ctl.pack(fill="x", padx=6, pady=(4, 0))
        ttk.Label(ctl, text="Levels shown:").pack(side="left")
        self.levels_var = tk.StringVar(value="3")
        sp = ttk.Spinbox(
            ctl,
            from_=1,
            to=12,
            width=3,
            textvariable=self.levels_var,
            command=self.draw_tree,
        )
        sp.pack(side="left", padx=(4, 10))
        sp.bind("<Return>", lambda e: self.draw_tree())
        ttk.Button(ctl, text="Back to full tree", command=self.reset_view).pack(
            side="left"
        )
        ttk.Separator(ctl, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Label(ctl, text="Zoom:").pack(side="left")
        ttk.Button(
            ctl, text="\u2212", width=3, command=lambda: self.zoom_by(1 / ZOOM_STEP)
        ).pack(side="left", padx=(4, 0))
        ttk.Button(
            ctl, text="+", width=3, command=lambda: self.zoom_by(ZOOM_STEP)
        ).pack(side="left", padx=2)
        ttk.Button(ctl, text="Fit all", command=self.fit_tree).pack(side="left", padx=2)
        ttk.Button(ctl, text="100%", width=5, command=lambda: self.set_zoom(1.0)).pack(
            side="left", padx=2
        )
        self.zoom_var = tk.StringVar(value="100%")
        ttk.Label(ctl, textvariable=self.zoom_var, width=6).pack(side="left")
        self.tree_info = tk.StringVar()
        ttk.Label(ctl, textvariable=self.tree_info, foreground="#555").pack(
            side="left", padx=10
        )

        ttk.Label(
            right,
            foreground="#555",
            text="\u25b2 MAX   \u25bc MIN   \u25a0 leaf (heuristic)   "
            "\u2717 pruned by alpha-beta   green = best line   "
            "click = board & H   double-click = open subtree   drag = move   "
            "Ctrl+wheel = zoom in/out",
        ).pack(anchor="w", padx=6, pady=(2, 4))

        holder = ttk.Frame(right)
        holder.pack(fill="both", expand=True, padx=6)
        self.tree_canvas = tk.Canvas(
            holder,
            width=720,
            height=380,
            bg="white",
            highlightthickness=1,
            highlightbackground="#bbb",
        )
        ysb = ttk.Scrollbar(holder, orient="vertical", command=self.tree_canvas.yview)
        xsb = ttk.Scrollbar(holder, orient="horizontal", command=self.tree_canvas.xview)
        self.tree_canvas.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree_canvas.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)

        c = self.tree_canvas
        c.bind("<ButtonPress-1>", self.on_tree_press)
        c.bind("<B1-Motion>", self.on_tree_drag)
        c.bind("<ButtonRelease-1>", self.on_tree_release)
        c.bind("<Double-Button-1>", self.on_tree_double)
        c.bind("<MouseWheel>", self.on_wheel)  # Windows / macOS
        c.bind("<Button-4>", lambda e: c.yview_scroll(-3, "units"))  # Linux
        c.bind("<Button-5>", lambda e: c.yview_scroll(3, "units"))
        c.bind("<Shift-Button-4>", lambda e: c.xview_scroll(-3, "units"))
        c.bind("<Shift-Button-5>", lambda e: c.xview_scroll(3, "units"))
        c.bind("<Shift-MouseWheel>", self.on_shift_wheel)  # Windows / macOS
        # zoom: Ctrl + wheel (anchored at the mouse pointer)
        c.bind("<Control-MouseWheel>", self.on_zoom_wheel)  # Windows / macOS
        c.bind(
            "<Control-Button-4>", lambda e: self.zoom_by(ZOOM_STEP, e.x, e.y)
        )  # Linux
        c.bind("<Control-Button-5>", lambda e: self.zoom_by(1 / ZOOM_STEP, e.x, e.y))
        # zoom: keyboard
        self.bind("<Control-plus>", lambda e: self.zoom_by(ZOOM_STEP))
        self.bind("<Control-equal>", lambda e: self.zoom_by(ZOOM_STEP))
        self.bind("<Control-minus>", lambda e: self.zoom_by(1 / ZOOM_STEP))
        self.bind("<Control-0>", lambda e: self.fit_tree())

        # selected-node details: board preview + heuristic values
        detail = ttk.LabelFrame(right, text=" Selected node: board & heuristic values ")
        detail.pack(fill="x", padx=6, pady=6)
        self.mini = tk.Canvas(
            detail, width=COL * MINI_CELL, height=ROWS * MINI_CELL, highlightthickness=0
        )
        self.mini.pack(side="left", padx=8, pady=8)
        self.detail_var = tk.StringVar(value="Click a node in the tree.")
        ttk.Label(
            detail, textvariable=self.detail_var, font=("Courier", 10), justify="left"
        ).pack(side="left", padx=8)

    # ------------------------------------------------------------ drawing
    def redraw(self):
        self.canvas.delete("all")
        draw_grid(self.canvas, self.board, CELL, top=HEADER)
        self.update_scores()

    def set_status(self, text):
        self.status.set(text)

    def update_scores(self):
        ai_w, hu_w = get_all_windows(self.board)
        self.score_var.set(
            f"Connected-fours  ->  AI: {ai_w[3]}   Human: {hu_w[3]}\n"
            f"Heuristic H(board) = {fmt(H(ai_w, hu_w))}"
        )

    # ------------------------------------------------------------ game flow
    def start_game(self):
        try:
            k = int(self.k_var.get())
            if k < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid K", "K must be an integer >= 1.")
            return
        if k > 7 and not messagebox.askyesno(
            "Large K", f"K = {k} may make the AI very slow. Continue?"
        ):
            return
        if self.busy and self.game_on:
            return  # AI is thinking, ignore

        self.k = k
        self.board = initilize_board()
        self.game_on = True
        self.clear_tree()
        self.stats_var.set("")
        self.redraw()

        if self.first_var.get() == "AI":
            self.ai_turn()
        else:
            self.busy = False
            self.set_status("Your turn - click a column.")

    def end_game(self):
        self.game_on = False
        self.busy = True
        ai_w, hu_w = get_all_windows(self.board)
        a, h = ai_w[3], hu_w[3]
        if a > h:
            result = "AI wins!"
        elif h > a:
            result = "You win!"
        else:
            result = "It's a draw."
        self.set_status(f"Board full - {result}   (AI {a} : {h} Human)")
        messagebox.showinfo(
            "Game over",
            f"{result}\n\nAI connected-fours: {a}\nHuman connected-fours: {h}",
        )

    # ------------------------------------------------------------ human input
    def column_at(self, x):
        c = int(x // CELL)
        return c if 0 <= c < COL else None

    def on_hover(self, event):
        self.canvas.delete("ghost")
        if self.busy or not self.game_on:
            return
        c = self.column_at(event.x)
        if c is None or c not in legalmove(self.board):
            return
        d = CELL - 2 * PAD
        x0 = c * CELL + PAD
        self.canvas.create_oval(
            x0,
            PAD,
            x0 + d,
            PAD + d,
            fill=C_HUMAN,
            outline=C_OUTLINE,
            width=2,
            tags="ghost",
        )

    def on_click(self, event):
        if self.busy or not self.game_on:
            return
        c = self.column_at(event.x)
        if c is None or c not in legalmove(self.board):
            self.bell()
            return
        self.busy = True
        self.canvas.delete("ghost")
        self.animate_drop(c, HUMAN, self.after_human_move)

    def after_human_move(self):
        if isboardfilled(self.board):
            self.end_game()
        else:
            self.ai_turn()

    # ------------------------------------------------------------ AI turn
    def ai_turn(self):
        self.busy = True
        self.set_status(f"AI is thinking (K = {self.k}) ...")
        self.config(cursor="watch")
        self._result = None
        snapshot = self.board.copy()

        def work():
            try:
                t0 = time.perf_counter()
                col, root = bestmove(snapshot, self.k)
                elapsed = time.perf_counter() - t0
                self._result = ("ok", col, root, elapsed, count_nodes(root))
            except Exception as exc:  # report it in the GUI thread
                self._result = ("error", exc)

        threading.Thread(target=work, daemon=True).start()
        self.after(60, self.poll_ai)

    def poll_ai(self):
        if self._result is None:
            self.after(60, self.poll_ai)
            return
        self.config(cursor="")
        res, self._result = self._result, None
        if res[0] == "error":
            self.game_on = False
            messagebox.showerror("AI error", str(res[1]))
            return

        _, col, root, elapsed, nodes = res
        self.show_tree(root)
        self.stats_var.set(
            f"Last AI move:  column {col + 1 if col is not None else '-'}\n"
            f"Time: {elapsed:.3f} s   Nodes expanded: {nodes}"
        )
        if col is None:
            self.end_game()
            return
        self.animate_drop(col, AI, self.after_ai_move)

    def after_ai_move(self):
        if isboardfilled(self.board):
            self.end_game()
        else:
            self.busy = False
            self.set_status("Your turn - click a column.")

    # ------------------------------------------------------------ animation
    def landing_row(self, col):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return None

    def animate_drop(self, col, player, done):
        """Let a disc fall, then place it on the real board via makemove()."""
        row = self.landing_row(col)
        d = CELL - 2 * PAD
        x0 = col * CELL + PAD
        target = HEADER + row * CELL + PAD
        state = {"y": float(PAD), "v": 4.0}
        item = self.canvas.create_oval(
            x0,
            state["y"],
            x0 + d,
            state["y"] + d,
            fill=piece_color(player),
            outline=C_OUTLINE,
            width=2,
            tags="fall",
        )

        def step():
            state["y"] += state["v"]
            state["v"] += 2.0
            if state["y"] >= target:
                self.canvas.delete(item)
                makemove(self.board, col, player)  # real move (board.py)
                self.redraw()
                done()
                return
            self.canvas.coords(item, x0, state["y"], x0 + d, state["y"] + d)
            self.after(14, step)

        step()

    # ------------------------------------------------------------ drawn tree
    def clear_tree(self):
        self.tree_canvas.delete("all")
        self.root_node = self.view_root = self.selected = None
        self.pv_ids = set()
        self.tag_node, self.node_pos = {}, {}
        self.tree_info.set("")
        self.mini.delete("all")
        self.detail_var.set("Click a node in the tree.")

    def show_tree(self, root):
        """Called after every AI move with the new minimax tree."""
        self.clear_tree()
        self.root_node = self.view_root = root

        # best line: from each node follow the first child with the same value
        n = root
        while n is not None:
            self.pv_ids.add(id(n))
            n = next((ch for ch in n.children if ch.value == n.value), None)

        # show as many levels as comfortably fit
        depth = max(1, min(tree_depth(root), 12))
        levels = 1
        for lv in range(2, depth + 1):
            if count_levels(root, lv) <= 1500:
                levels = lv
            else:
                break
        self.levels_var.set(str(levels))
        self.draw_tree()
        self.select_node(root)

    def reset_view(self):
        if self.root_node is not None:
            self.view_root = self.root_node
            self.draw_tree()

    def draw_tree(self):
        c = self.tree_canvas
        c.delete("all")
        self.tag_node, self.node_pos = {}, {}
        self._texts = []
        self._zoom = 1.0  # the layout below is drawn at 100%
        if self.view_root is None:
            return
        try:
            levels = int(self.levels_var.get())
        except ValueError:
            levels = 3
        levels = max(1, min(levels, 12))
        reduced = False
        while levels > 1 and count_levels(self.view_root, levels) > MAX_DRAWN:
            levels -= 1
            reduced = True
        self.levels_var.set(str(levels))

        nodes, edges, prunes = [], [], []
        self._slot = 0

        def next_x():
            x = LEFT + self._slot * X_GAP
            self._slot += 1
            return x

        def rec(node, level):
            """Lay out a node; returns its x. Leaves get consecutive slots,
            parents are centred over their children."""
            y = TOP + level * LEVEL_H
            child_x, links, pruned = [], [], []
            collapsed = bool(node.children) and level >= levels
            if level < levels:
                for ch in node.children:
                    cx = rec(ch, level + 1)
                    child_x.append(cx)
                    links.append((ch, cx))
                if node.cutoff:
                    # alpha-beta stopped: the columns never expanded were pruned
                    used = {ch.move for ch in node.children}
                    for col in legalmove(node.board):
                        if col not in used:
                            px = next_x()
                            child_x.append(px)
                            pruned.append((col, px))
            x = (child_x[0] + child_x[-1]) / 2 if child_x else next_x()
            for ch, cx in links:
                best = id(node) in self.pv_ids and id(ch) in self.pv_ids
                edges.append((x, y, cx, y + LEVEL_H, ch.move, best))
            for col, px in pruned:
                prunes.append((x, y, px, y + LEVEL_H, col))
            nodes.append((node, x, y, collapsed))
            return x

        root_x = rec(self.view_root, 0)

        # 1) edges  2) pruned branches  3) nodes (on top)
        for x1, y1, x2, y2, col, best in edges:
            c.create_line(
                x1,
                y1 + R,
                x2,
                y2 - R,
                fill=C_PV if best else "#888",
                width=3 if best else 1,
            )
            self._edge_label(x1, y1 + R, x2, y2 - R, col, "#222")
        for x1, y1, x2, y2, col in prunes:
            c.create_line(x1, y1 + R, x2, y2 - R, fill=C_PRUNE, dash=(3, 3))
            self._edge_label(x1, y1 + R, x2, y2 - R, col, C_PRUNE)
            self._txt(x2, y2, "\u2717", 20, True, C_PRUNE)

        for i, (node, x, y, collapsed) in enumerate(nodes):
            tag = f"nd{i}"
            self.tag_node[tag] = node
            self.node_pos[id(node)] = (x, y)
            best = id(node) in self.pv_ids
            outline, width = (C_PV, 3) if best else ("#333", 1.5)
            if not node.children:  # leaf: heuristic / terminal
                c.create_rectangle(
                    x - R + 2,
                    y - R + 2,
                    x + R - 2,
                    y + R - 2,
                    fill=C_LEAF,
                    outline=outline,
                    width=width,
                    tags=(tag,),
                )
            elif is_max_node(node):  # MAX: triangle pointing up
                c.create_polygon(
                    x,
                    y - R,
                    x - R - 2,
                    y + R,
                    x + R + 2,
                    y + R,
                    fill=C_MAX,
                    outline=outline,
                    width=width,
                    tags=(tag,),
                )
            else:  # MIN: triangle pointing down
                c.create_polygon(
                    x,
                    y + R,
                    x - R - 2,
                    y - R,
                    x + R + 2,
                    y - R,
                    fill=C_MIN,
                    outline=outline,
                    width=width,
                    tags=(tag,),
                )
            self._txt(x, y + R + 11, fmt(node.value), 9, best, "#000", (tag,))
            if collapsed:
                self._txt(x, y + R + 24, "+ more", 8, False, "#777", (tag,))

        # unzoomed size of the whole tree, then apply the default zoom
        self._base = (self._slot * X_GAP + 2 * LEFT, TOP + levels * LEVEL_H + 50)
        c.update_idletasks()
        self.set_zoom(DEFAULT_ZOOM)  # start at 50%; "Fit all" shows everything

        note = f"{len(nodes)} nodes drawn, {len(prunes)} pruned branches"
        if reduced:
            note += f"  (levels reduced to {levels}: too many nodes)"
        self.tree_info.set(note)
        if self.selected is not None:
            self._draw_ring(self.selected)

    def _edge_label(self, x1, y1, x2, y2, col, color):
        """Column number written on an edge."""
        lx = x1 + (x2 - x1) * 0.7
        ly = y1 + (y2 - y1) * 0.7
        self.tree_canvas.create_rectangle(
            lx - 7, ly - 7, lx + 7, ly + 7, fill="white", outline=""
        )
        self._txt(lx, ly, str(col + 1), 9, False, color)

    # ------------------------------------------------------------ zoom
    def _txt(self, x, y, text, size, bold=False, fill="#000", tags=()):
        """Create a label that is remembered so its font can follow the zoom."""
        item = self.tree_canvas.create_text(
            x,
            y,
            text=text,
            fill=fill,
            tags=tags,
            font=("Helvetica", size, "bold" if bold else "normal"),
        )
        self._texts.append((item, size, bold))
        return item

    def _update_fonts(self):
        c, z = self.tree_canvas, self._zoom
        for item, size, bold in self._texts:
            s = size * z
            if s < 5:  # too small to read: hide the label
                c.itemconfigure(item, state="hidden")
            else:
                c.itemconfigure(
                    item,
                    state="normal",
                    font=("Helvetica", int(round(s)), "bold" if bold else "normal"),
                )

    def set_zoom(self, new_zoom, cx=None, cy=None):
        """Zoom the drawn tree to `new_zoom` (1.0 = 100%).
        (cx, cy) = window pixel that must stay fixed (default: top-left)."""
        c = self.tree_canvas
        if self.view_root is None:
            return
        new_zoom = max(ZOOM_MIN, min(ZOOM_MAX, new_zoom))
        f = new_zoom / self._zoom
        if cx is not None:
            px, py = c.canvasx(cx), c.canvasy(cy)  # point under the mouse (before)
        c.scale("all", 0, 0, f, f)
        self._zoom = new_zoom
        self._update_fonts()

        cw, ch = max(c.winfo_width(), 1), max(c.winfo_height(), 1)
        w, h = self._base[0] * new_zoom, self._base[1] * new_zoom
        left = min(0.0, (w - cw) / 2)  # centre the tree if it is smaller
        right = left + max(w, cw)  # than the window
        bottom = max(h, ch)
        c.configure(scrollregion=(left, 0, right, bottom))
        if cx is None:
            c.xview_moveto(0)
            c.yview_moveto(0)
        else:  # keep the pointed spot in place
            c.xview_moveto((px * f - cx - left) / (right - left))
            c.yview_moveto((py * f - cy) / bottom)
        self.zoom_var.set(f"{new_zoom * 100:.0f}%")
        if self.selected is not None:
            self._draw_ring(self.selected)

    def zoom_by(self, factor, cx=None, cy=None):
        c = self.tree_canvas
        if cx is None:  # buttons: zoom around the centre
            cx, cy = c.winfo_width() / 2, c.winfo_height() / 2
        self.set_zoom(self._zoom * factor, cx, cy)

    def fit_tree(self):
        """Zoom out (never in) until the whole tree fits in the window."""
        if self.view_root is None:
            return
        c = self.tree_canvas
        cw, ch = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        bw, bh = self._base
        self.set_zoom(min(1.0, (cw - 4) / bw, (ch - 4) / bh))

    def on_zoom_wheel(self, event):
        self.zoom_by(ZOOM_STEP if event.delta > 0 else 1 / ZOOM_STEP, event.x, event.y)

    def on_shift_wheel(self, event):
        self.tree_canvas.xview_scroll(-3 if event.delta > 0 else 3, "units")

    # ------------------------------------------------------------ tree input
    def node_at(self, event):
        c = self.tree_canvas
        x, y = c.canvasx(event.x), c.canvasy(event.y)
        for item in reversed(c.find_overlapping(x - 3, y - 3, x + 3, y + 3)):
            for tag in c.gettags(item):
                if tag in self.tag_node:
                    return self.tag_node[tag]
        return None

    def on_tree_press(self, event):
        self._press = (event.x, event.y, False)
        self.tree_canvas.scan_mark(event.x, event.y)

    def on_tree_drag(self, event):
        if self._press is None:
            return
        x0, y0, moved = self._press
        if moved or abs(event.x - x0) > 3 or abs(event.y - y0) > 3:
            self._press = (x0, y0, True)
            self.tree_canvas.scan_dragto(event.x, event.y, gain=1)

    def on_tree_release(self, event):
        if self._press is not None and not self._press[2]:
            node = self.node_at(event)
            if node is not None:
                self.select_node(node)
        self._press = None

    def on_tree_double(self, _event):
        node = self.node_at(_event)
        if node is not None and node.children:
            self.view_root = node  # zoom into this sub-tree
            self.draw_tree()

    def on_wheel(self, event):
        self.tree_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    # ------------------------------------------------------------ selection
    def _draw_ring(self, node):
        c = self.tree_canvas
        c.delete("sel")
        pos = self.node_pos.get(id(node))
        if pos:
            x, y = pos
            z = self._zoom
            c.create_rectangle(
                z * (x - R - 7),
                z * (y - R - 7),
                z * (x + R + 7),
                z * (y + R + 22),
                outline="#ff8800",
                width=2,
                dash=(4, 2),
                tags="sel",
            )

    def select_node(self, node):
        """Show the board and the heuristic values of a tree node."""
        self.selected = node
        self._draw_ring(node)
        self.mini.delete("all")
        draw_grid(self.mini, node.board, MINI_CELL, top=0, pad=3)

        ai_w, hu_w = get_all_windows(node.board)
        who = (
            "root (current board)"
            if node.player is None
            else f"{'AI' if node.player == AI else 'HUMAN'} played column {node.move + 1}"
        )
        lines = [
            f"Node       : {who}",
            f"Node value : {fmt(node.value)}",
            f"H(board)   : {fmt(H(ai_w, hu_w))}",
            "",
            "Pieces in an open 4-window:",
            "  n   AI   Human   weight",
        ]
        for i in range(4):
            lines.append(f"  {i + 1}  {ai_w[i]:>3}   {hu_w[i]:>4}   {weight[i]:.2f}")
        lines.append("H = sum Wn * (AI_n - Human_n)")
        self.detail_var.set("\n".join(lines))


if __name__ == "__main__":
    Connect4GUI().mainloop()
