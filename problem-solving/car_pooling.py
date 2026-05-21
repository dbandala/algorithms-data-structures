# 1094. Car Pooling
# There is a car with capacity empty seats. The vehicle only drives east (i.e., it cannot turn around and drive west).

# You are given the integer capacity and an array trips where trips[i] = [numPassengersi, fromi, toi] indicates that the ith trip has numPassengersi passengers and the locations to pick them up and drop them off are fromi and toi respectively. The locations are given as the number of kilometers due east from the car's initial location.

# Return true if it is possible to pick up and drop off all passengers for all the given trips, or false otherwise.


# Example 1:
# Input: trips = [[2,1,5],[3,3,7]], capacity = 4
# Output: false

# Example 2:
# Input: trips = [[2,1,5],[3,3,7]], capacity = 5
# Output: true

# Constraints:
# 1 <= trips.length <= 1000
# trips[i].length == 3
# 1 <= numPassengersi <= 100
# 0 <= fromi < toi <= 1000
# 1 <= capacity <= 105


class Solution(object):
    def carPooling(self, trips, capacity):
        """
        :type trips: List[List[int]]
        :type capacity: int
        :rtype: bool
        """

        delta = [0]*1001 # route

        for passengers, start, end in trips:
            delta[start] += passengers
            delta[end] -= passengers

        current = 0
        for change in delta:
            current += change
            if current>capacity:
                return False

        return True



class SparseCoordinatesSolution(object):
    def carPooling(self, trips, capacity):
        """
        :type trips: List[List[int]]
        :type capacity: int
        :rtype: bool
        """

        events = []
        for passengers, start, end in trips:
            events.append((start, passengers))
            events.append((end, -passengers))

        events.sort()

        current = 0
        i = 0
        while i < len(events):
            loc = events[i][0]
            # apply all changes at this location
            while i < len(events) and events[i][0] == loc:
                current += events[i][1]
                i += 1
            if current > capacity:
                return False
        
        return True






sol = Solution()
trips = [[2,1,5],[3,3,7]]
capacity = 4
print(sol.carPooling(trips, capacity)) # false

trips = [[2,1,5],[3,3,7]]
capacity = 5
print(sol.carPooling(trips, capacity)) # true

