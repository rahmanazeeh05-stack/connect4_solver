class Node:

    def __init__(self, board, depth, player, move=None):

        self.board = board.copy()
        self.depth = depth
        self.player = player
        self.move = move

        self.value = None
        self.children = []

        self.cutoff = False
        self.is_leaf = False


def print_tree(node, prefix="", is_last=True, is_root=True):

    if is_root:

        print(f"ROOT | Depth: {node.depth} | Minimax: {node.value}")

    else:

        branch = "└── " if is_last else "├── "

        player_name = "AI" if node.player == 1 else "HUMAN"

        value_type = "Heuristic" if node.is_leaf else "Minimax"

        print(
            prefix + branch +
            f"{player_name} | Column: {node.move} | "
            f"Depth: {node.depth} | "
            f"{value_type}: {node.value}"
        )

    if node.cutoff:
        print(prefix + "    [alphabeta cutoff]")

    if is_root:
        new_prefix = ""
    else:
        new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node.children):

        last_child = (i == len(node.children) - 1)

        print_tree(
            child,
            new_prefix,
            last_child,
            False
        )