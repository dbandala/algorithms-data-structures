# Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.


class Solution(object):
    def trap(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        # verify edge cases
        if len(height) < 2:
            return 0
        
        # initialize variables
        left_max = [0 for _ in range(len(height))]
        right_max = [0 for _ in range(len(height))]
        water = 0

        # calculate the left max
        left_max[0] = height[0]
        for i in range(1, len(height)):
            left_max[i] = max(left_max[i-1], height[i])

        print("left_max: ", left_max)

        # calculate the right max
        right_max[-1] = height[-1]
        for i in range(len(height)-2, -1, -1):
            right_max[i] = max(right_max[i+1], height[i])

        print("right_max: ", right_max)

        print("height: ", height)

        water_path = []
        # calculate the water
        for i in range(len(height)):
            water += min(left_max[i], right_max[i]) - height[i]
            water_path.append(min(left_max[i], right_max[i]) - height[i])

        print("water_path: ", water_path)
        return water

    def trap_two_pointers(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        if not height:
            return 0
        if len(height) < 2:
            return 0

        left, right = 0, len(height)-1
        left_max, right_max = 0, 0
        water = 0

        while left<right:
            # if the left height is less than the right height, we can trap water on the left
            if height[left]<height[right]:
                # update the left max
                if height[left]>=left_max:
                    left_max = height[left]
                else:
                    # trap water on the left
                    water += left_max - height[left]
                left += 1
            else:
                # if the right height is less than the left height, we can trap water on the right
                if height[right]>=right_max:
                    # update the right max
                    right_max = height[right]
                else:
                    # trap water on the right
                    water += right_max - height[right]
                right -= 1
        return water

# Test cases
sol = Solution()
print(sol.trap([0,1,0,2,1,0,1,3,2,1,2,1])) # 6
print(sol.trap_two_pointers([0,1,0,2,1,0,1,3,2,1,2,1])) # 6
