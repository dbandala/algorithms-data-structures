class Solution(object):
    def asteroidCollision(self, asteroids):
        """
        :type asteroids: List[int]
        :rtype: List[int]
        """
        # first we check edge cases
        if len(asteroids) <= 0:
            return []
        
        # remove ceros from asteroids - sanity check
        asteroids_clean = [ast for ast in asteroids if ast!=0]

        # if there are no asteroids, return empty list
        if len(asteroids_clean) == 0:
            return []
        
        # if there is only one asteroid, return the asteroid
        if len(asteroids_clean) == 1:
            return asteroids_clean
        
        # if there are two asteroids, check if they collide
        if len(asteroids_clean) == 2:
            if asteroids_clean[0] > 0 and asteroids_clean[1] < 0:
                return [max(asteroids_clean)] if abs(asteroids_clean[0])!=abs(asteroids_clean[1]) else []
            else:
                return asteroids_clean
        
        # if there are more than two asteroids, we need to check for collisions
        stack = []
        for ast in asteroids_clean:
            if ast > 0:
                stack.append(ast)
            else:
                while len(stack) > 0 and stack[-1] > 0:
                    if stack[-1] == abs(ast):
                        stack.pop()
                        break
                    elif stack[-1] < abs(ast):
                        stack.pop()
                    else:
                        break
                else:
                    stack.append(ast)
        return stack
    


# Test cases
sol = Solution()
print(sol.asteroidCollision([5, 10, -5])) # [5, 10]
print(sol.asteroidCollision([8, -8])) # []
print(sol.asteroidCollision([10, 2, -5])) # [10]
#print(sol.asteroidCollision([-2, 4, -1, 1, 2])) # [-2, -1, 1, 2]
#print(sol.asteroidCollision([-2,-1,1,2])) # [-2, -2, -2]
#print(sol.asteroidCollision([-2, -2, 1, -1])) # [-2, -2, -1]
print(sol.asteroidCollision([10, 2, -4]))

