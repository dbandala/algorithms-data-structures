# You are given m arrays, where each array is sorted in ascending order.
# You can pick up two integers from two different arrays (each array picks one) and calculate the distance. We define the distance between two integers a and b to be their absolute difference |a - b|.

# Return the maximum distance.

class Solution(object):
    def maxDistance(self, arrays):
        """
        :type arrays: List[List[int]]
        :rtype: int
        """
        if not arrays:
            return 0
        if len(arrays) == 1:
            return 0
        if len(arrays[0]) == 0:
            return 0
        max_distance = 0
        min_val = arrays[0][0]
        max_val = arrays[0][-1]
        for i in range(1, len(arrays)):
            max_distance = max(max_distance, max(abs(arrays[i][-1] - min_val), abs(max_val - arrays[i][0])))
            min_val = min(min_val, arrays[i][0])
            max_val = max(max_val, arrays[i][-1])

        print(f"""min_val: {min_val}, max_val: {max_val}""")
        return max_distance

class NaiveSolution(object):
    def maxDistance(self, arrays):
        """
        :type arrays: List[List[int]]
        :rtype: int
        """
        if not arrays:
            return 0
        if len(arrays) == 1:
            return 0
        if len(arrays[0]) == 0:
            return 0
        max_distance = 0
        for i in range(len(arrays)):
            if not arrays[i]:
                continue
            for j in range(i+1, len(arrays)):
                max_distance = max(max_distance, abs(arrays[i][-1] - arrays[j][0]))
                max_distance = max(max_distance, abs(arrays[j][-1] - arrays[i][0]))
        return max_distance


# Test cases
sol = Solution()
print(sol.maxDistance([[1,2,3],[4,5],[1,2,3]])) # 4
print(sol.maxDistance([[1,4],[0,5]])) # 4
print(sol.maxDistance([[1,5],[3,4]])) # 3

print(sol.maxDistance([[-8,-7,-7,-5,1,1,3,4],[-2],[-10,-10,-7,0,1,3],[2]])) # 14

