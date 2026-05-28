# 994. Rotting Oranges
# You are given an m x n grid where each cell can have one of three values:

# 0 representing an empty cell,
# 1 representing a fresh orange, or
# 2 representing a rotten orange.
# Every minute, any fresh orange that is 4-directionally adjacent to a rotten orange becomes rotten.

# Return the minimum number of minutes that must elapse until no cell has a fresh orange. If this is impossible, return -1.

# Example 1:
# Input: grid = [[2,1,1],[1,1,0],[0,1,1]]
# Output: 4

# Example 2:
# Input: grid = [[2,1,1],[0,1,1],[1,0,1]]
# Output: -1
# Explanation: The orange in the bottom left corner (row 2, column 0) is never rotten, because rotting only happens 4-directionally.

# Example 3:
# Input: grid = [[0,2]]
# Output: 0
# Explanation: Since there are already no fresh oranges at minute 0, the answer is just 0.


class Solution(object):
    def rottingOranges(self, grid)-> int:
        """
        :type grid: list[list[int]]
        :rtype: int
        """
        # verify edge cases
        if not grid:
            return 0
        if len(grid) == 0:
            return 0
        if len(grid[0]) == 0:
            return 0

        # we are going to use breadth

        self.m, self.n = len(grid), len(grid[0])
        self.grid = grid
        self.visited = [[False for _ in range(self.n)] for _ in range(self.m)]

        self.clock = 0 # counter of minutes

        self.queue = {0: []} # for bfs

        # find seed points
        no_fresh_oranges = True
        for i in range(self.m):
            for j in range(self.n):
                if grid[i][j]==2:
                    self.queue[0].append((i,j))
                    self.visited[i][j] = True
                if grid[i][j]==1:
                    no_fresh_oranges = False
        
        # case where all oranges are rotten
        if no_fresh_oranges:
            return 0
        
        # flood rotten oranges
        self.bfs()

        print(self.grid)

        # verify if there still at least one fresh orange
        for i in range(self.m):
            for j in range(self.n):
                if grid[i][j]==1:
                    return -1

        # return total minutes
        return self.clock-1
        
        

    def bfs(self):
        cycle = 0
        rotten_oranges = self.queue.get(cycle, [])
        while len(rotten_oranges)>0:
            cycle += 1
            self.clock += 1
            self.queue[cycle] = []
            while len(rotten_oranges)>0:
                i, j = rotten_oranges.pop()
                # up
                if i>0 and self.grid[i-1][j]==1 and not self.visited[i-1][j]:
                    self.queue[cycle].append((i-1,j))
                    self.visited[i-1][j] = True
                    self.grid[i-1][j] = 2
                # right
                if j<self.n-1 and self.grid[i][j+1]==1 and not self.visited[i][j+1]:
                    self.queue[cycle].append((i,j+1))
                    self.visited[i][j+1] = True
                    self.grid[i][j+1] = 2
                # down
                if i<self.m-1 and self.grid[i+1][j]==1 and not self.visited[i+1][j]:
                    self.queue[cycle].append((i+1,j))
                    self.visited[i+1][j] = True
                    self.grid[i+1][j] = 2
                # left
                if j>0 and self.grid[i][j-1]==1 and not self.visited[i][j-1]:
                    self.queue[cycle].append((i,j-1))
                    self.visited[i][j-1] = True
                    self.grid[i][j-1] = 2
            # next cycle
            rotten_oranges = self.queue.get(cycle, [])

class OptimalSolution(object):
    def rottingOranges(self, grid):
        """
        Multi-source BFS using two frontiers per minute (no deque).
        """
        if not grid or not grid[0]:
            return 0

        m, n = len(grid), len(grid[0])
        current = []
        fresh = 0

        for i in range(m):
            for j in range(n):
                if grid[i][j] == 2:
                    current.append((i, j))
                elif grid[i][j] == 1:
                    fresh += 1

        if fresh == 0:
            return 0

        minutes = 0
        while current:
            minutes += 1
            nxt = []
            for i, j in current:
                for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] == 1:
                        grid[ni][nj] = 2
                        fresh -= 1
                        nxt.append((ni, nj))
            current = nxt

        return minutes - 1 if fresh == 0 else -1
            


sol = Solution()

grid = [[2,1,1],[1,1,0],[0,1,1]]
print(sol.rottingOranges(grid)) # 4





