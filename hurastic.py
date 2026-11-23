import numpy as np

EMPTY = 0
AI = 1
HUMAN = 2
ROWS = 6
COLS = 7
WINDSIZE = 4

W1 = 3
W2 = 4
W3 = 5
W4 = 6


weight = np.array([W1, W2, W3, W4])


def H(ai, human):
    """Dot product to get sum from k = 1 -> 4 (Wk * (N_ai_k - N_human_K))"""
    return weight @ ((ai - human))


def get_all_windows(state):

    ai = np.zeros(4, dtype=int)
    human = np.zeros(4, dtype=int)

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(ROWS):
        for c in range(COLS):

            for dr, dc in directions:

                cells = []

                for i in range(WINDSIZE):
                    newr = r + i * dr
                    newc = c + i * dc

                    if not (0 <= newr < ROWS and 0 <= newc < COLS):
                        break

                    cells.append(state[newr][newc])

                if len(cells) != WINDSIZE:
                    continue

                ai_count = cells.count(AI)
                human_count = cells.count(HUMAN)

                if ai_count > 0 and human_count > 0:
                    continue
                else:
                    if ai_count > 0:
                        ai[ai_count - 1] += 1
                    elif human_count > 0:
                        human[human_count - 1] += 1
                    else:
                        continue

    return ai, human
