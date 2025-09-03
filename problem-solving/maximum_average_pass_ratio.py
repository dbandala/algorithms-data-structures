# 1792. Maximum Average Pass Ratio

# There is a school that has classes of students and each class will be having a final exam. You are given a 2D integer array classes, where classes[i] = [passi, totali]. You know beforehand that in the ith class, there are totali total students, but only passi number of students will pass the exam.
# You are also given an integer extraStudents. There are another extraStudents brilliant students that are guaranteed to pass the exam of any class they are assigned to. You want to assign each of the extraStudents students to a class in a way that maximizes the average pass ratio across all the classes.
# The pass ratio of a class is equal to the number of students of the class that will pass the exam divided by the total number of students of the class. The average pass ratio is the sum of pass ratios of all the classes divided by the number of the classes.
# Return the maximum possible average pass ratio after assigning the extraStudents students. Answers within 10-5 of the actual answer will be accepted.

# Example 1:
# Input: classes = [[1,2],[3,5],[2,2]], extraStudents = 2
# Output: 0.78333
# Explanation: You can assign the two extra students to the first class. The average pass ratio will be equal to (3/4 + 3/5 + 2/2) / 3 = 0.78333.

# Example 2:
# Input: classes = [[2,4],[3,9],[4,5],[2,10]], extraStudents = 4
# Output: 0.53485
 
# Constraints:
# 1 <= classes.length <= 105
# classes[i].length == 2
# 1 <= passi <= totali <= 105
# 1 <= extraStudents <= 105

import heapq


class Solution(object):
    def maxAverageRatio(self, classes, extraStudents):
        """
        :type classes: List[List[int]]
        :type extraStudents: int
        :rtype: float
        """
        heap = []
        for pass_students, total_students in classes:
            improvement = self.calculate_pass_ratio(pass_students, total_students)
            heapq.heappush(heap, (-improvement, pass_students, total_students))

        # Distribute extra students
        while extraStudents > 0 and heap:
            improvement, pass_students, total_students = heapq.heappop(heap)
            improvement = -improvement

            # Assign an extra student to this class
            pass_students += 1
            total_students += 1
            extraStudents -= 1

            # Recalculate the improvement and push it back into the heap
            new_improvement = self.calculate_pass_ratio(pass_students, total_students)
            heapq.heappush(heap, (-new_improvement, pass_students, total_students))

        # print("heap: ", heap)

        # Calculate the final average pass ratio
        total_pass_ratio = sum(1.0 * pass_students / total_students for _, pass_students, total_students in heap)
        return total_pass_ratio / len(classes)
    
    def calculate_pass_ratio(self, pass_students, total_students):
        return (1.0 * (pass_students + 1) / (total_students + 1)) - (1.0 * pass_students / total_students)

# This algorithm has a complexity of O(n log n) due to the heap operations.


class SolutionWithoutHeap(object):
    def maxAverageRatio(self, classes, extraStudents):
        """
        :type classes: List[List[int]]
        :type extraStudents: int
        :rtype: float
        """
        total_pass_ratio = 0
        for pass_students, total_students in classes:
            total_pass_ratio += pass_students / total_students

        # Distribute extra students evenly
        while extraStudents > 0:
            for i in range(len(classes)):
                if extraStudents == 0:
                    break
                classes[i][0] += 1
                classes[i][1] += 1
                extraStudents -= 1

        # Calculate the final average pass ratio
        total_pass_ratio = sum(pass_students / total_students for pass_students, total_students in classes)
        return total_pass_ratio / len(classes)
    """
        This algorithm has a complexity of O(n) due to the simple iteration and arithmetic operations.
    """


# Test Cases
print(Solution().maxAverageRatio([[1,2],[3,5],[2,2]], 2))  # Expected output: 0.78333
print(Solution().maxAverageRatio([[2,4],[3,9],[4,5],[2,10]], 4))  # Expected output: 0.53485


print(SolutionWithoutHeap().maxAverageRatio([[1,2],[3,5],[2,2]], 2))  # Expected output: 0.78333
print(SolutionWithoutHeap().maxAverageRatio([[2,4],[3,9],[4,5],[2,10]], 4))  # Expected output: 0.53485
