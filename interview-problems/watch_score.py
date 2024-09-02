#!/bin/python3

# Complete the 'getMinScore' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER_ARRAY watch_history
#  2. INTEGER series1
#  3. INTEGER series2
#

def getMinScore(watch_history, series1, series2):
    # input:
    #   watch_history: list
    #   series1: int
    #   series2: int
    # return: int (minimum watch score)
    # first approach: use a sliding window to explore all contiguous sublist
    
    # verify edge cases
    n = len(watch_history)
    if n==0:
        return 0
    if n==1:
        return 1
        
    if series1 is None or series2 is None or series1 not in watch_history or series2 not in watch_history:
        return 0
    
    # minimum_score = n
    # for i in range(n-1):
    #     for j in range(i+1, n):
    #         distinct_series = {} # dictionary to store values
    #         for k in range(i, j):
    #             if watch_history[k] not in distinct_series:
    #                 distinct_series[watch_history[k]] = 0
    #             else:
    #                 distinct_series[watch_history[k]] += 1
    #         if series1 in distinct_series and series2 in distinct_series:
    #             minimum_score = min(minimum_score, len(distinct_series))

    # another approach
    # iterate through the watch history
    # store the indexes of the series1 and series2 in the watch history
    # if both series1 and series2 are found, calculate the minimum score
    # return the minimum score
    series1_index = -1
    series2_index = -1
    minimum_score = n
    for i in range(n):
        if watch_history[i] == series1:
            series1_index = i
        if watch_history[i] == series2:
            series2_index = i
        if series1_index != -1 and series2_index != -1:
            minimum_score = min(minimum_score, abs(series1_index - series2_index) + 1)
            
    return minimum_score
            
            

# Test cases
# Test case 1
watch_history = [1, 2, 1, 3, 4, 2, 3]
series1 = 1
series2 = 2
# Expected output: 3
print(getMinScore(watch_history, series1, series2))

# Test case 2
watch_history = [1, 2, 1, 3, 4, 2, 3]
series1 = 1
series2 = 3
# Expected output: 4
print(getMinScore(watch_history, series1, series2))

# Test case 3
watch_history = [1, 2, 4, 3, 4, 2, 3]
series1 = 1
series2 = 3
# Expected output: 4
print(getMinScore(watch_history, series1, series2))
