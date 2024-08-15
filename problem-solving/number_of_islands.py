# Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.
# An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.

class Solution(object):
    def numIslands(self, grid):
        """
        :type grid: List[List[str]]
        :rtype: int
        """
        # first we check edge cases
        if len(grid) == 0:
            return 0
        if len(grid[0]) == 0:
            return 0
        
        self.grid = grid
        self.visited = [[False for _ in range(len(grid[0]))] for _ in range(len(grid))]
        
        # we will use a depth-first search to find the islands
        islands = 0
        for i in range(len(grid)):
            row_sum = sum([int(x) for x in grid[i]])
            for j in range(len(grid[0])):
                visited_sum = sum([int(x) for x in self.visited[i]])
                if row_sum == visited_sum:
                    break
                if grid[i][j] == '1' and not self.visited[i][j]:
                    islands += 1
                    self.dfs(i, j)
        return islands

    def dfs(self, i, j):
        self.visited[i][j] = True
        if i > 0 and self.grid[i-1][j] == '1' and not self.visited[i-1][j]:
            self.dfs(i-1, j) # up
        if i < len(self.grid)-1 and self.grid[i+1][j] == '1' and not self.visited[i+1][j]:
            self.dfs(i+1, j) # down
        if j > 0 and self.grid[i][j-1] == '1' and not self.visited[i][j-1]:
            self.dfs(i, j-1) # left
        if j < len(self.grid[0])-1 and self.grid[i][j+1] == '1' and not self.visited[i][j+1]:
            self.dfs(i, j+1) # right
        

# Test cases O(n*m)
sol = Solution()
grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]
print("Solution output: ", sol.numIslands(grid)) # 1
grid = [["1","1","1"],["0","1","0"],["0","1","0"]]
print("Solution output: ", sol.numIslands(grid)) # 1