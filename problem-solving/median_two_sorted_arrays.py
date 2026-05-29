# Leetcode 4. Median of Two Sorted Arrays
# Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.
# Follow up: The overall run time complexity should be O(log (m+n)).

# Example 1:
# Input: nums1 = [1,3], nums2 = [2]
# Output: 2.00000
# Explanation: merged array = [1,2,3] and median is 2.

# Example 2:
# Input: nums1 = [1,2], nums2 = [3,4]
# Output: 2.50000
# Explanation: merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.

# Constraints:
# nums1.length == m
# nums2.length == n
# 0 <= m <= 1000
# 0 <= n <= 1000
# 1 <= m + n <= 2000
# -106 <= nums1[i], nums2[i] <= 106


class Solution(object):
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        # validate edge cases
        if not nums1 and not nums2:
            return 0.0
        if not nums1:
            return self.get_median(nums2)
        
        if not nums2:
            return self.get_median(nums1)
        
        merged = self.merge_sort(nums1 + nums2)
        return self.get_median(merged)

    def get_median(self, arr):
        n = len(arr)
        if n % 2 == 0: # even number of elements
            return (arr[n//2] + arr[n//2 - 1]) / 2
        else:
            return arr[n//2]
            
    
    def merge_sort(self, arr):
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]
        
        left_half = self.merge_sort(left_half)
        right_half = self.merge_sort(right_half)
        
        return self.merge(left_half, right_half)

    def merge(self, left, right):
        merged = []
        left_index = 0
        right_index = 0
        
        while left_index < len(left) and right_index < len(right):
            if left[left_index] < right[right_index]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1
        
        while left_index < len(left):
            merged.append(left[left_index])
            left_index += 1
        
        while right_index < len(right):
            merged.append(right[right_index])
            right_index += 1
        
        return merged


class OptimizedSolution(object): # O(log(n+m))
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        m, n = len(nums1), len(nums2)
        # edge cases
        if m==0 and n==0:
            return 0.0
        # if n==0:
        #     return nums1[m//2]
        # if m==0:
        #     return nums2[n//2]

        # partition on smaller array
        if m>n:
            nums1, nums2 = nums2, nums1
            m, n = len(nums1), len(nums2)

        # Idea: Partition nums1 at index i and nums2 at index j such that the left halves together have exactly (m+n)//2 elements, and max(left_half) <= min(right_half). Binary search on i in the shorter array.

        h, l = m, 0
        while l<=h:
            # pick a partion in nums1
            px = (h+l)//2
            # pick a partition in nums2 forced by px
            # we need at least (m+n)//2 in left halves
            py= (m+n+1)//2 - px

            # bounding limits - window - inf -> partition at border of array
            max_left_x = -float('inf') if px==0 else nums1[px-1]
            min_right_x = float('inf') if px==m else nums1[px]
            max_left_y = -float('inf') if py==0 else nums2[py-1]
            min_right_y = float('inf') if py==n else nums2[py]

            # validate partitions
            if (max_left_x<=min_right_y and max_left_y<=min_right_x):
                if (m+n)%2 == 0:
                    return (max(max_left_x, max_left_y)+min(min_right_x, min_right_y)) / 2.0
                else:
                    return max(max_left_x, max_left_y)

            # adjust window
            if (max_left_x > min_right_y):
                h = px - 1 # partition in nums1 too big
            else:
                l = px + 1 # partition in nums1 too small
            

    

# Test cases
sol = Solution()
nums1 = [1,2]
nums2 = [3,4]
print(sol.findMedianSortedArrays(nums1, nums2)) # 2.5


sol = OptimizedSolution()
nums1 = [1,2]
nums2 = [3,4]
print(sol.findMedianSortedArrays(nums1, nums2)) # 2.5

nums1 = [1,3]
nums2 = [2]
print(sol.findMedianSortedArrays(nums1, nums2)) # 2.0

nums1 = [0,0]
nums2 = [0,0]
print(sol.findMedianSortedArrays(nums1, nums2)) # 0.0

nums1 = [1,3]
nums2 = [2,7]
print(sol.findMedianSortedArrays(nums1, nums2)) # 2.5
