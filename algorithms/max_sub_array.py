# List: Max Sub Array ( ** Interview Question)
# Given an array of integers nums, write a function max_subarray(nums) that finds the contiguous subarray (containing at least one number) with the largest sum and returns its sum.

def max_subarray(nums):
    # edge cases
    if len(nums) == 0:
        return 0
    if len(nums) == 1:
        return nums[0]
    # initialize the maximum subarray sum and the current subarray sum
    max_sum = current_sum = nums[0]
    # iterate through the array starting from the second element
    for num in nums[1:]:
        # update the current subarray sum by taking the maximum of the current number and the current number plus the current subarray sum
        current_sum = max(num, current_sum + num)
        # update the maximum subarray sum by taking the maximum of the current subarray sum and the maximum subarray sum
        max_sum = max(max_sum, current_sum)
    # return the maximum subarray sum
    return max_sum

# Example 1: Simple case with positive and negative numbers
input_case_1 = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
result_1 = max_subarray(input_case_1)
print("Example 1: Input:", input_case_1, "\nResult:", result_1)  

# Example 2: Case with a negative number in the middle
input_case_2 = [1, 2, 3, -4, 5, 6]
result_2 = max_subarray(input_case_2)
print("Example 2: Input:", input_case_2, "\nResult:", result_2) 

# Example 3: Case with all negative numbers
input_case_3 = [-1, -2, -3, -4, -5]
result_3 = max_subarray(input_case_3)
print("Example 3: Input:", input_case_3, "\nResult:", result_3) 


"""
    EXPECTED OUTPUT:
    ----------------
    Example 1: Input: [-2, 1, -3, 4, -1, 2, 1, -5, 4] 
    Result: 6
    Example 2: Input: [1, 2, 3, -4, 5, 6] 
    Result: 13
    Example 3: Input: [-1, -2, -3, -4, -5] 
    Result: -1
    
"""