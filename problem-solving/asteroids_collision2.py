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

        # split asteroids going right and left
        asteroids_going_right = []
        asteroids_going_left = []

        for asteroid in asteroids_clean:
            if asteroid>=0:
                asteroids_going_right.append(asteroid)
            else:
                asteroids_going_left.append(asteroid)

        # collide asteroids
        for i in range(len(asteroids_going_right)):
            if (len(asteroids_going_right)==0 or i>len(asteroids_going_right)):
                break
            ast_right_size = asteroids_going_right[len(asteroids_going_right)-1-i]
            for j in range(len(asteroids_going_left)):
                if (len(asteroids_going_left)==0 or j>=len(asteroids_going_left)):
                    break
                ast_left_size = abs(asteroids_going_left[j])
                if (ast_right_size>ast_left_size):
                    asteroids_going_left.pop(0)
                elif (ast_right_size<ast_left_size):
                    asteroids_going_right.pop()
                elif (ast_right_size==ast_left_size):
                    asteroids_going_right.pop()
                    asteroids_going_left.pop(0)

        return asteroids_going_right+asteroids_going_left


# Test cases
sol = Solution()
#print(sol.asteroidCollision([5, 10, -5])) # [5, 10]
#print(sol.asteroidCollision([8, -8])) # []
#print(sol.asteroidCollision([10, 2, -5])) # [10]
#print(asteroidCollision([-2, 4, -1, 1, 2])) # [-2, -1, 1, 2]
#print(sol.asteroidCollision([-2, -2, 1, -2])) # [-2, -2, -2]
#print(sol.asteroidCollision([-2, -2, 1, -1])) # [-2, -2, -1]


