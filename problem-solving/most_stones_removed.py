# Leetcode 947. Most Stones Removed with Same Row or Column
# On a 2D plane, we place n stones at some integer coordinate points. Each coordinate point may have at most one stone.
# A stone can be removed if it shares either the same row or the same column as another stone that has not been removed.
# Given an array stones of length n where stones[i] = [xi, yi] represents the location of the ith stone, return the largest possible number of stones that can be removed.



# Example 1:

# Input: stones = [[0,0],[0,1],[1,0],[1,2],[2,1],[2,2]]
# Output: 5
# Explanation: One way to remove 5 stones is as follows:
# 1. Remove stone [2,2] because it shares the same row as [2,1].
# 2. Remove stone [2,1] because it shares the same column as [0,1].
# 3. Remove stone [1,2] because it shares the same row as [1,0].
# 4. Remove stone [1,0] because it shares the same column as [0,0].
# 5. Remove stone [0,1] because it shares the same row as [0,0].
# Stone [0,0] cannot be removed since it does not share a row/column with another stone still on the plane.
# Example 2:

# Input: stones = [[0,0],[0,2],[1,1],[2,0],[2,2]]
# Output: 3
# Explanation: One way to make 3 moves is as follows:
# 1. Remove stone [2,2] because it shares the same row as [2,0].
# 2. Remove stone [2,0] because it shares the same column as [0,0].
# 3. Remove stone [0,2] because it shares the same row as [0,0].
# Stones [0,0] and [1,1] cannot be removed since they do not share a row/column with another stone still on the plane.
# Example 3:

# Input: stones = [[0,0]]
# Output: 0
# Explanation: [0,0] is the only stone on the plane, so you cannot remove it.
 

# Constraints:

# 1 <= stones.length <= 1000
# 0 <= xi, yi <= 104
# No two stones are at the same coordinate point.


class Solution(object):
    def removeStones(self, stones):
        """
        :type stones: List[List[int]]
        :rtype: int
        """

        n = len(stones)

        # Adjacency list to store graph connections
        adjacency_list = [[] for _ in range(n)]

        # Build the graph: Connect stones that share the same row or column
        for i in range(n):
            for j in range(i + 1, n):
                if stones[i][0] == stones[j][0] or stones[i][1] == stones[j][1]:
                    adjacency_list[i].append(j)
                    adjacency_list[j].append(i)

        num_of_connected_components = 0
        visited = [False] * n

        # DFS to visit all stones in a connected component
        def _depth_first_search(stone):
            visited[stone] = True
            for neighbor in adjacency_list[stone]:
                if not visited[neighbor]:
                    _depth_first_search(neighbor)

        # Traverse all stones using DFS to count connected components
        for i in range(n):
            if not visited[i]:
                _depth_first_search(i)
                num_of_connected_components += 1

        # Maximum stones that can be removed is total stones minus number of connected components
        return n - num_of_connected_components
    


# Time complexity: O(N^2)
# Space complexity: O(N^2)
# where N is the number of stones in the input array. The adjacency list will have a maximum of N^2 edges in the worst case. The DFS will visit each stone only once, so the time complexity is O(N^2) and the space complexity is O(N^2).

# Test cases
if __name__ == "__main__":
    solution = Solution()
    # Test case 1
    stones = [[0,0],[0,1],[1,0],[1,2],[2,1],[2,2]]
    # Expected output: 5
    print(solution.removeStones(stones))
    # Test case 2
    stones = [[0,0],[0,2],[1,1],[2,0],[2,2]]
    # Expected output: 3
    print(solution.removeStones(stones))
    # Test case 3
    stones = [[0,0]]
    # Expected output: 0
    print(solution.removeStones(stones))
    # Test case 4
    stones = [[0,0],[0,1],[1,0],[1,1],[2,1],[2,2]]
    # Expected output: 4
    print(solution.removeStones(stones))
    # Test case 5
    stones = [[0,0],[0,1],[1,0],[1,1],[2,1],[2,2],[3,3],[3,4],[4,3],[4,4]]
    # Expected output: 6
    print(solution.removeStones(stones))
    # Test case 6
    stones = [[0,0],[0,1],[1,0],[1,1],[2,1],[2,2],[3,3],[3,4],[4,3],[4,4],[5,5],[5,6],[6,5],[6,6]]
    # Expected output: 8
    print(solution.removeStones(stones))
    # Test case 7
    stones = [[0,0],[0,1],[1,0],[1,1],[2,1],[2,2],[3,3],[3,4],[4,3],[4,4],[5,5],[5,6],[6,5],[6,6],[7,7],[7,8],[8,7],[8,8]]
    # Expected output: 10
    print(solution.removeStones(stones))
    # Test case 8
    stones = [[0,0],[0,1],[1,0],[1,1],[2,1],[2,2],[3,3],[3,4],[4,3],[4,4],[5,5],[5,6],[6,5],[6,6],[7,7],[7,8],[8,7],[8,8],[9,9],[9,10],[10,9],[10,10]]
    # Expected output: 12
    print(solution.removeStones(stones))
        

