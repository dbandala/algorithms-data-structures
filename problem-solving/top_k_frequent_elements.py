# 347. Top K Frequent Elements
# Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.

# Example 1:
# Input: nums = [1,1,1,2,2,3], k = 2
# Output: [1,2]

# Example 2:
# Input: nums = [1], k = 1
# Output: [1]

# Example 3:
# Input: nums = [1,2,1,2,1,2,3,1,3,2], k = 2
# Output: [1,2]


# Constraints:
# 1 <= nums.length <= 105
# -104 <= nums[i] <= 104
# k is in the range [1, the number of unique elements in the array].
# It is guaranteed that the answer is unique.
 

# Follow up: Your algorithm's time complexity must be better than O(n log n), where n is the array's size.

import heapq

class Solution(object):
    def topKFrequent(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: List[int]
        """
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1
        return sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:k]

# bucket sort approach
class BucketSortSolution(object):
    def topKFrequent(self, nums, k):
        """
        :type nums: List[int] 
        :type k: int
        :rtype: List[int]
        """
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1
        # buckets[i] = list of numbers that appear exactly i times
        # index goes from 0 to len(nums) — frequency is bounded by n
        buckets = [[] for _ in range(len(nums) + 1)]
        for num, count in freq.items():
            buckets[count].append(num)
        # Collect from highest frequency buckets down
        result = []
        for i in range(len(buckets) - 1, 0, -1):
            for num in buckets[i]:
                result.append(num)
                if len(result) == k:
                    return result

# Heap solution
class HeapSolution(object):
    def topKFrequent(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: List[int]
        """
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1
        heap = []
        for num, count in freq.items():
            heapq.heappush(heap, (-count, num))
        result = []
        for _ in range(k):
            result.append(heapq.heappop(heap)[1])
        return result

# Test cases
sol = Solution()
nums = [1,1,1,2,2,3]
k = 2
print(sol.topKFrequent(nums, k)) # [1,2]

nums = [1]
k = 1
print(sol.topKFrequent(nums, k)) # [1]

nums = [1,2,1,2,1,2,3,1,3,2]
k = 2
print(sol.topKFrequent(nums, k)) # [1,2]

# Bucket sort solution
bucket_sol = BucketSortSolution()
print(bucket_sol.topKFrequent(nums, k)) # [1,2]

# Heap solution
heap_sol = HeapSolution()
print(heap_sol.topKFrequent(nums, k)) # [1,2]