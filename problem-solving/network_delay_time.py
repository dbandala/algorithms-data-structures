# 743. Network Delay Time
# You are given a network of n nodes, labeled from 1 to n. You are also given times, a list of travel times as directed edges times[i] = (ui, vi, wi), where ui is the source node, vi is the target node, and wi is the time it takes for a signal to travel from source to target.

# We will send a signal from a given node k. Return the minimum time it takes for all the n nodes to receive the signal. If it is impossible for all the n nodes to receive the signal, return -1.

# Example 1:
# Input: times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
# Output: 2

# Example 2:
# Input: times = [[1,2,1]], n = 2, k = 1
# Output: 1

# Example 3:
# Input: times = [[1,2,1]], n = 2, k = 2
# Output: -1


# Constraints:
# 1 <= k <= n <= 100
# 1 <= times.length <= 6000
# times[i].length == 3
# 1 <= ui, vi <= n
# ui != vi
# 0 <= wi <= 100
# All the pairs (ui, vi) are unique. (i.e., no multiple edges.)



import re


class Solution(object):
    def networkDelayTime(self,
        times: list[list[int]],
        n: int,
        k: int) -> int:
        """
        :type times: list[list[int]] (ui, vi, wi)
        :type n: int
        :type k: int
        :rtype: int
        """

        if len(times)==0:
            if n<=1:
                return 0
            else:
                return -1


        distances = [float('inf')]*n
        distances[k-1] = 0

        visited = [False]*n

        for _ in range(n):
            min_distance = float('inf')
            u = None

            print(distances)
            for i in range(n):
                if not visited[i] and distances[i]<min_distance:
                    min_distance = distances[i]
                    u = i
            
            if u == None:
                break

            visited[u] = True

            for ui, vi, wi in times:
                ui -= 1
                vi -= 1
                if ui==u and not visited[vi]:
                    alt = distances[u]+wi
                    if alt<distances[vi]:
                        distances[vi] = alt

        for dist in distances:
            if dist == float('inf'):
                return -1

        return max(distances)



sol = Solution()

times = [[2,1,1],[2,3,1],[3,4,1]]
print(sol.networkDelayTime(times, 4, 2)) # 2


times = [[3,5,78],[2,1,1],[1,3,0],[4,3,59],[5,3,85],[5,2,22],[2,4,23],[1,4,43],[4,5,75],[5,1,15],[1,5,91],[4,1,16],[3,2,98],[3,4,22],[5,4,31],[1,2,0],[2,5,4],[4,2,51],[3,1,36],[2,3,59]]
print(sol.networkDelayTime(times, 5, 5)) # 31



