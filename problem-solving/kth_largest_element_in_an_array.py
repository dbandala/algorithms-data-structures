# 215. Kth Largest Element in an Array

# Given an integer array nums and an integer k, return the kth largest element in the array.

# Note that it is the kth largest element in the sorted order, not the kth distinct element.

# Can you solve it without sorting?

# Example 1:
# Input: nums = [3,2,1,5,6,4], k = 2
# Output: 5

# Example 2:
# Input: nums = [3,2,3,1,2,4,5,5,6], k = 4
# Output: 4
 
# Constraints:
# 1 <= k <= nums.length <= 105
# -104 <= nums[i] <= 104

import heapq

# time complexity O(n log(k))
# space complexity O(k)
class Solution(object):
    def largestElement(self, nums, k):
        """
        type nums: list[int]
        type k: int
        rtype: int
        """
        # edge cases
        if len(nums)==0 or k==0:
            return 0

        # approach A: min-heap of size k
        heap_min = []

        for num in nums:
            heapq.heappush(heap_min, num)
            if len(heap_min)>k:
                heapq.heappop(heap_min)

        return heapq.heappop(heap_min)



