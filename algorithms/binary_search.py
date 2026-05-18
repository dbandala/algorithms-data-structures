# Standard binary search on a sorted array

# iterative template

def binary_search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2   # avoids integer overflow (critical in Java/C++)

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1    # target must be in right half
        else:
            right = mid - 1   # target must be in left half

    return -1   # not found