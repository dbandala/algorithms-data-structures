# Given an m x n grid of characters board and a string word, return true if word exists in the grid.
# The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.

class Solution(object):
    def exist(self, board, word):
        """
        :input board: List[List[str]] (m*n)
        :input word: str
        :return: bool
        """
        # verify edge cases
        if len(board) == 0:
            return False
        if len(board[0]) == 0:
            return False
        if len(word) == 0:
            return False
        
        self.board = board
        self.word = word

        self.visited = [[False for _ in range(len(board[0]))] for _ in range(len(board))]

        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.dfs(i, j, 0): return True
        return False
                
    def dfs(self, i, j, k):
        if (k == len(self.word)):
            return True
        if i<0 or j<0 or i>=len(self.board) or j>=len(self.board[0]) or self.word[k]!=self.board[i][j] or self.visited[i][j]:
            return False
        self.visited[i][j] = True
        res = self.dfs(i-1, j, k+1) or self.dfs(i+1, j, k+1) or self.dfs(i, j-1, k+1) or self.dfs(i, j+1, k+1)
        self.visited[i][j] = False
        return res

# Test cases
sol = Solution()
# board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
# word = "ABCCED"
# print("Solution output: ", sol.exist(board, word)) # True

# board = [["A","B","C","E"],["S","F","E","S"],["A","D","E","E"]]
# word = "ABCESEEEFS"
# print("Solution output: ", sol.exist(board, word)) # True

board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
word = "SEE"
print("Solution output: ", sol.exist(board, word)) # True