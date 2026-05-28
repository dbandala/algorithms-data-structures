# 621. Task Scheduler

# You are given an array of CPU tasks, each labeled with a letter from A to Z, and a number n. Each CPU interval can be idle or allow the completion of one task. Tasks can be completed in any order, but there's a constraint: there has to be a gap of at least n intervals between two tasks with the same label.

# Return the minimum number of CPU intervals required to complete all tasks.

# Example 1:
# Input: tasks = ["A","A","A","B","B","B"], n = 2
# Output: 8
# Explanation: A possible sequence is: A -> B -> idle -> A -> B -> idle -> A -> B.
# After completing task A, you must wait two intervals before doing A again. The same applies to task B. In the 3rd interval, neither A nor B can be done, so you idle. By the 4th interval, you can do A again as 2 intervals have passed.

# Example 2:
# Input: tasks = ["A","C","A","B","D","B"], n = 1
# Output: 6
# Explanation: A possible sequence is: A -> B -> C -> D -> A -> B.
# With a cooling interval of 1, you can repeat a task after just one other task.

# Example 3:
# Input: tasks = ["A","A","A", "B","B","B"], n = 3
# Output: 10
# Explanation: A possible sequence is: A -> B -> idle -> idle -> A -> B -> idle -> idle -> A -> B.
# There are only two types of tasks, A and B, which need to be separated by 3 intervals. This leads to idling twice between repetitions of these tasks.


# Constraints:
# 1 <= tasks.length <= 104
# tasks[i] is an uppercase English letter.
# 0 <= n <= 100

import heapq
from collections import deque

class Solution(object):
    def leastInterval(self, tasks, n):
        """
        :type tasks: List[str]
        :type n: int
        :rtype: int
        """
        # edge case
        if len(tasks)==0:
            return 0
        # approach: greedy + max-heap
        # we count the required tasks we should complete
        tasks_counter = {}
        for task in tasks:
            tasks_counter[task] = tasks_counter.get(task, 0) + 1

        # *** Always schedule the most frequent task that is available (cooldown expired)
        max_heap = [-c for c in tasks_counter.values()]
        heapq.heapify(max_heap)

        time = 0
        cooldown = deque[int, int]() # (remaining_count, available_at)

        while max_heap or cooldown:
            time += 1

            while cooldown and cooldown[0][1]<=time:
                ready_count, _ = cooldown.popleft()
                heapq.heappush(max_heap, ready_count)

            if max_heap:
                cnt = heapq.heappop(max_heap) + 1
                if cnt!=0:
                    cooldown.append((cnt, time+n+1))
        return time


# test cases
sol = Solution()
print(sol.leastInterval(["A","A","A","B","B","B"], 2)) # 8
print(sol.leastInterval(["A","C","A","B","D","B"], 1)) # 6
print(sol.leastInterval(["A","A","A", "B","B","B"], 3)) # 10





