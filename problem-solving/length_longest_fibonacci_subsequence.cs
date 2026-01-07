// 873. Length of Longest Fibonacci Subsequence
// A sequence x1, x2, ..., xn is Fibonacci-like if:
// n >= 3
// xi + xi+1 == xi+2 for all i + 2 <= n

// Given a strictly increasing array arr of positive integers forming a sequence, return the length of the longest Fibonacci-like subsequence of arr. If one does not exist, return 0.
// A subsequence is derived from another sequence arr by deleting any number of elements (including none) from arr, without changing the order of the remaining elements. For example, [3, 5, 8] is a subsequence of [3, 4, 5, 6, 7, 8].

// Example 1:
// Input: arr = [1,2,3,4,5,6,7,8]
// Output: 5
// Explanation: The longest subsequence that is fibonacci-like: [1,2,3,5,8].

// Example 2:
// Input: arr = [1,3,7,11,12,14,18]
// Output: 3
// Explanation: The longest subsequence that is fibonacci-like: [1,11,12], [3,11,14] or [7,11,18].

// Constraints:
// 3 <= arr.length <= 1000
// 1 <= arr[i] < arr[i + 1] <= 109

using System;
using System.Collections.Generic;
using System.Linq;

public class Solution
{
    public int LenLongestFibSubseq(int[] arr)
    {
        var index = new Dictionary<int, int>();
        for (int i = 0; i < arr.Length; i++)
        {
            index[arr[i]] = i;
        }
        
        int n = arr.Length;
        var longest = new Dictionary<(int, int), int>();
        int maxLength = 0;
        
        for (int k = 0; k < n; k++)
        {
            for (int j = 0; j < k; j++)
            {
                int iVal = arr[k] - arr[j];
                if (iVal < arr[j] && index.ContainsKey(iVal))
                {
                    int i = index[iVal];
                    int length = longest.ContainsKey((i, j)) ? longest[(i, j)] + 1 : 3;
                    longest[(j, k)] = length;
                    maxLength = Math.Max(maxLength, length);
                }
            }
        }
        
        return maxLength >= 3 ? maxLength : 0;
    }
}

public class NaiveSolution
{
    public int LenLongestFibSubseq(int[] arr)
    {
        int n = arr.Length;
        int maxLength = 0;
        var arrSet = new HashSet<int>(arr);
        
        for (int i = 0; i < n; i++)
        {
            for (int j = i + 1; j < n; j++)
            {
                int a = arr[i];
                int b = arr[j];
                int length = 2;
                
                while (arrSet.Contains(a + b))
                {
                    int temp = a;
                    a = b;
                    b = temp + b;
                    length++;
                }
                
                if (length >= 3)
                {
                    maxLength = Math.Max(maxLength, length);
                }
            }
        }
        
        return maxLength >= 3 ? maxLength : 0;
    }
}

// Test cases
public class Program
{
    public static void Main()
    {
        var sol = new Solution();
        
        int[] arr1 = { 1, 2, 3, 4, 5, 6, 7, 8 };
        Console.WriteLine(sol.LenLongestFibSubseq(arr1));  // Output: 5
        
        int[] arr2 = { 1, 3, 7, 11, 12, 14, 18 };
        Console.WriteLine(sol.LenLongestFibSubseq(arr2));  // Output: 3
    }
}
