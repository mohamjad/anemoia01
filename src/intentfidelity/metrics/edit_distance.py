from __future__ import annotations


def edit_distance(reference: tuple[str, ...], hypothesis: tuple[str, ...]) -> int:
    rows = len(reference) + 1
    cols = len(hypothesis) + 1
    matrix = [[0] * cols for _ in range(rows)]
    for row in range(rows):
        matrix[row][0] = row
    for col in range(cols):
        matrix[0][col] = col
    for row in range(1, rows):
        for col in range(1, cols):
            substitution = 0 if reference[row - 1] == hypothesis[col - 1] else 1
            matrix[row][col] = min(
                matrix[row - 1][col] + 1,
                matrix[row][col - 1] + 1,
                matrix[row - 1][col - 1] + substitution,
            )
    return matrix[-1][-1]


def normalized_edit_distance(reference: tuple[str, ...], hypothesis: tuple[str, ...]) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return edit_distance(reference, hypothesis) / len(reference)

