# Volvo interview problem
# You are given a string s and two-dimensional array of characters of size NxN named grid. Each field in the grid is either empty (denoted by a dot .) or contains uppercase english letter. Each particular letter may appear at most twice in the grid.
# Your task is to construct string s by visiting fields of the grid. You start the reconstruction with an empty string. You can choose the field in which you want to start. In one move you can change the current field to an adjacent one (up, down, left, right). If you visit a field containing a letter, you may append this letter to the end of the reconstructed string. Appending a letter is not counted as a move. Each field can be visited and each letter can be used multiple times during reconstruction process.
# what is the minimum number of moves needed to reconstruct the string s?
# write a function
# def solution(S, grid)
# that given a string s and an array grid, returns the minimum number of moves needed to reconstruct the string s. If it is impossible to reconstruct the string s, return -1.
# Examples:
# 1. Given s = "AB", grid = ["AB", "CD"], the function should return 1. You can start in the upper-left corner and visit both letters in one move.
# 2. Given s = "ABCA", grid = [".A.C", ".B..","....","...A"], the function should return 6. You can start in the upper-left corner and visit all letters in 6 moves.
# 3. Given s = "KLLRML", grid = ["K....", "S...L","....R","LX...","XM..S"], the function should return 13. You can start in the upper-left corner and visit all letters in 13 moves.


def _manhattan(a, b):
    """Return the minimum grid moves between two cells using Manhattan distance."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _build_letter_positions(grid):
    """Map each letter in the grid to its coordinates (at most two per letter)."""
    letter_positions = {}
    for i, row in enumerate(grid):
        for j, letter in enumerate(row):
            if letter != ".":
                letter_positions.setdefault(letter, []).append((i, j))
    return letter_positions


def solution(S, grid):
    """
    Return the minimum number of moves needed to reconstruct S on the grid.

    Each letter appears at most twice, so we track the minimum cost to end at
    each possible position for the current character in S. Transitions between
    different characters add Manhattan distance; repeated characters cost 0.
    """
    if not S:
        return 0

    letter_positions = _build_letter_positions(grid)

    print("letter_positions: ", letter_positions)

    if S[0] not in letter_positions:
        return -1

    # dp[position] = min moves to reconstruct S[0:i+1] ending at position
    dp = {pos: 0 for pos in letter_positions[S[0]]}

    print("dp: ", dp)

    for i in range(1, len(S)):
        if S[i] == S[i - 1]:
            continue

        if S[i] not in letter_positions:
            return -1

        next_dp = {}
        for cur_pos in letter_positions[S[i]]:
            next_dp[cur_pos] = min(
                prev_cost + _manhattan(prev_pos, cur_pos)
                for prev_pos, prev_cost in dp.items()
            )
        dp = next_dp

    return min(dp.values())


# Test cases
if __name__ == "__main__":
    print(solution("AB", ["A..B", "C..D", "Q..B", "A..Z"]))  # 3
    # print(solution("AB", ["AB", "CD"]))  # 1
    # print(solution("ABCA", [".A.C", ".B..", "....", "...A"]))  # 6
    # print(solution("KLLRML", ["K....", "S...L", "....R", "LX...", "XM..S"]))  # 13
