# Volvo interview problem
# You are given a string s and two-dimensional array of characters of size NxN named grid. Each field in the grid is either empty (denoted by a dot .) or contains uppercase english letter. Each particular letter may appear at most twice in the grid.
# Your task is to construct string s by visiting fields of the grid. You start the reconstruction with an empty string. You can choose the field in which you want to start. In one move you can change the current field to an adjacent one (up, down, left, right). If you visit a field containing a letter, you may append this letter to the end of the reconstructed string. Appending a letter is not counted as a move. Each field can be visited and each letter can be used multiple times during reconstruction process.
# what is the minimum number of moves needed to reconstruct the string s?
# write a function
# def solution(S, grid)
# that given a string s and an array grid, returns the minimum number of moves needed to reconstruct the string s. If it is impossible to reconstruct the string s, return -1.
# Examples:
# 1. Given s = "AB", grid = ["AB", "CD"], the function should return 1. You can start in the upper-left corner and visit both letters in one move.

def naiveSolution(S, grid):
    # approach: dfs starting from initial char in the string
    grid_array = [list(row) for row in grid]
    n = len(grid_array)
    m = len(grid_array[0])
    max_moves = 0

    def _dfs(i, j, k, counter, track):

        print(i, j, k, counter)

        if k==len(S):
            return counter
        if i<0 or j<0 or i>=n or j>=m: # or grid_array[i][j]!=S[k]:
            return 0
        if grid_array[i][j]!=S[k] and grid_array[i][j]!=".":
            return 0
        if grid_array[i][j]==S[k]:
            k += 1
        
        # cells can be visited multiple times
        # do not dfs on previously visited cells
        # down = _dfs(i+1, j, k, counter, track) if 
        return min(_dfs(i+1, j, k, counter+1), _dfs(i-1, j, k, counter+1), _dfs(i, j+1, k, counter+1), _dfs(i, j-1, k, counter+1))
        
    for i in range(n):
        for j in range(m):
            if grid_array[i][j]==S[0]:
                max_moves = _dfs(i, j, 0, 0, [(i,j)])

    return max_moves if max_moves!=0 else -1


# another solution O(n*m + len(S))
def solution(S, grid):
    # approach: store the indexes of the characters in the grid
    # and find the minimum number of moves needed to reconstruct the string s
    letter_positions = {}
    grid_array = [list(row) for row in grid]
    n = len(grid_array)
    m = len(grid_array[0])

    for i in range(n):
        for j in range(m):
            letter = grid_array[i][j]
            if letter!='.':
                letter = grid_array[i][j]
                if letter not in letter_positions:
                    letter_positions[letter] = [(i,j)]
                else:
                    letter_positions[letter].append((i,j))

    #print(letter_positions)
    # if the first letter of string is not in grid
    if S[0] not in letter_positions:
        return -1
    
    total_moves = 0
    prev_char_pos = letter_positions[S[0]][0]
    for char_index in range(1, len(S)):
        prev_char = S[char_index-1]
        char = S[char_index]
        if char == prev_char:
            continue
        if char not in letter_positions:
            return -1
        # calculate distance between letters
        min_distance = float('inf')
        #prev_char_pos = letter_positions[prev_char][0]
        for char_pos in letter_positions[char]:
            distance = abs(prev_char_pos[0]-char_pos[0]) + abs(prev_char_pos[1]-char_pos[1])
            if distance < min_distance:
                min_distance = distance
                
            min_distance = min(min_distance, distance)

        total_moves += min_distance

    return total_moves


# Test cases
if __name__ == "__main__":
    print(solution("AB", ["A..B", "C..D", "Q..B", "A..Z"])) # 3
    print(solution("AB", ["AB", "CD"])) # 1
    print(solution("ABCA", [".A.C", ".B..","....","...A"])) # 6
    print(solution("KLLRML", ["K....", "S...L","....R","LX...","XM..S"])) # 13