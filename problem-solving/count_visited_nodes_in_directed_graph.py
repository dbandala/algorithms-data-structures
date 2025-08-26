# 2876. Count Visited Nodes in a Directed Graph

# There is a directed graph consisting of n nodes numbered from 0 to n - 1 and n directed edges.

# You are given a 0-indexed array edges where edges[i] indicates that there is an edge from node i to node edges[i].

# Consider the following process on the graph:

# You start from a node x and keep visiting other nodes through edges until you reach a node that you have already visited before on this same process.
# Return an array answer where answer[i] is the number of different nodes that you will visit if you perform the process starting from node i.

# Constraints:
# n == edges.length
# 2 <= n <= 105
# 0 <= edges[i] <= n - 1
# edges[i] != i


class NaiveSolution(object):
    def countVisitedNodes(self, edges):
        """
        :type edges: List[int]
        :rtype: List[int]
        """
        # verify edge cases
        if not edges:
            return []
        
        n = len(edges)

        answer = [0] * n
        
        # we need to detect a cycle in the directed graph
        def dfs(node, visited, counter):
            if visited[node]:
                return counter
            next_node = edges[node]
            visited[node] = True
            counter += 1
            return dfs(next_node, visited, counter)
        
        for i in range(n):
            visited = [False for _ in range(n)]
            answer[i] = dfs(i, visited, 0)


        return answer
    
    
    
class Solution(object):
    def countVisitedNodes(self, edges):
        """
        :type edges: List[int]
        :rtype: List[int]
        """
        if not edges:
            return []
        
        n = len(edges)
        answer = [0] * n
        visited = [False] * n
        
        for start in range(n):
            if visited[start]:
                continue
                
            # Find the cycle in this component
            path = []
            current = start
            node_to_index = {}
            
            # Traverse until we find a cycle or reach a visited node
            while current not in node_to_index and not visited[current]:
                node_to_index[current] = len(path)
                path.append(current)
                current = edges[current]
            
            if visited[current]:
                # We reached an already processed node
                cycle_start_answer = answer[current]
                for i in range(len(path) - 1, -1, -1):
                    node = path[i]
                    answer[node] = cycle_start_answer + (len(path) - i)
                    visited[node] = True
            else:
                # We found a cycle within this path
                cycle_start_idx = node_to_index[current]
                cycle_length = len(path) - cycle_start_idx
                
                # First, set answers for nodes in the cycle
                for i in range(cycle_start_idx, len(path)):
                    node = path[i]
                    answer[node] = cycle_length
                    visited[node] = True
                
                # Then, set answers for nodes leading to the cycle
                for i in range(cycle_start_idx - 1, -1, -1):
                    node = path[i]
                    answer[node] = cycle_length + (cycle_start_idx - i)
                    visited[node] = True
        
        return answer
    

# Test cases
sol = Solution()
print(sol.countVisitedNodes([1, 2, 0]))  # Output: [3, 3, 3]
print(sol.countVisitedNodes([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))  # Output: [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
print(sol.countVisitedNodes([2, 0, 1]))  # Output: [3, 3, 3]
print(sol.countVisitedNodes([1,2,0,0]))  # Output: [3,3,3,4]
