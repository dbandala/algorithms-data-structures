/**
 * Implementation of quick sort algorithm
 * Quick sort is a divide and conquer algorithm that was invented by Tony Hoare in 1960.
 * It is an efficient, general-purpose, comparison-based sorting algorithm.
 * Complexity: O(n log n)
 * Space complexity: O(log n)
 */
import java.util.Arrays;

public class QuickSort {
    
    /**
     * Quick sort algorithm implementation
     * @param arr the array to be sorted
     * @return sorted array
     */
    public static int[] quickSort(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        // Create a copy to avoid modifying the original array
        int[] result = Arrays.copyOf(arr, arr.length);
        quickSortHelper(result, 0, result.length - 1);
        return result;
    }
    
    /**
     * Helper method for quick sort using in-place sorting
     * @param arr the array to be sorted
     * @param low starting index
     * @param high ending index
     */
    private static void quickSortHelper(int[] arr, int low, int high) {
        if (low < high) {
            // Partition the array and get the pivot index
            int pivotIndex = partition(arr, low, high);
            
            // Recursively sort elements before and after partition
            quickSortHelper(arr, low, pivotIndex - 1);
            quickSortHelper(arr, pivotIndex + 1, high);
        }
    }
    
    /**
     * Partition method using Lomuto partition scheme
     * @param arr the array to partition
     * @param low starting index
     * @param high ending index
     * @return the partition index
     */
    private static int partition(int[] arr, int low, int high) {
        // Choose the rightmost element as pivot
        int pivot = arr[high];
        
        // Index of smaller element, indicates the right position of pivot found so far
        int i = low - 1;
        
        for (int j = low; j <= high - 1; j++) {
            // If current element is smaller than or equal to pivot
            if (arr[j] <= pivot) {
                i++; // increment index of smaller element
                swap(arr, i, j);
            }
        }
        swap(arr, i + 1, high);
        return i + 1;
    }
    
    /**
     * Utility method to swap two elements in an array
     * @param arr the array
     * @param i first index
     * @param j second index
     */
    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
    
    /**
     * Alternative implementation using the same approach as Python version
     * Creates new arrays for left, middle, and right partitions
     * @param arr the array to be sorted
     * @return sorted array
     */
    public static int[] quickSortPythonStyle(int[] arr) {
        if (arr.length <= 1) {
            return arr;
        }
        
        int pivot = arr[arr.length / 2];
        
        // Count elements for each partition
        int leftCount = 0, middleCount = 0, rightCount = 0;
        for (int x : arr) {
            if (x < pivot) leftCount++;
            else if (x == pivot) middleCount++;
            else rightCount++;
        }
        
        // Create arrays for each partition
        int[] left = new int[leftCount];
        int[] middle = new int[middleCount];
        int[] right = new int[rightCount];
        
        // Fill the partition arrays
        int leftIndex = 0, middleIndex = 0, rightIndex = 0;
        for (int x : arr) {
            if (x < pivot) {
                left[leftIndex++] = x;
            } else if (x == pivot) {
                middle[middleIndex++] = x;
            } else {
                right[rightIndex++] = x;
            }
        }
        
        // Recursively sort left and right, then combine
        int[] sortedLeft = quickSortPythonStyle(left);
        int[] sortedRight = quickSortPythonStyle(right);
        
        // Combine all arrays
        int[] result = new int[arr.length];
        System.arraycopy(sortedLeft, 0, result, 0, sortedLeft.length);
        System.arraycopy(middle, 0, result, sortedLeft.length, middle.length);
        System.arraycopy(sortedRight, 0, result, sortedLeft.length + middle.length, sortedRight.length);
        
        return result;
    }
    
    /**
     * Test cases
     */
    public static void main(String[] args) {
        int[] myList = {5, 3, 8, 6, 7, 2, 6, 2, 8, 8, 1, 4};
        
        System.out.println("Original array: " + Arrays.toString(myList));
        
        // Test in-place quick sort
        int[] sorted1 = quickSort(myList);
        System.out.println("Sorted (in-place): " + Arrays.toString(sorted1));
        
        // Test Python-style quick sort
        int[] sorted2 = quickSortPythonStyle(myList);
        System.out.println("Sorted (Python-style): " + Arrays.toString(sorted2));
        
        // Expected output: [1, 2, 2, 3, 4, 5, 6, 6, 7, 8, 8, 8]
    }
}

// 1. Save the code in a file named QuickSort.java
// 2. Open a terminal and navigate to the directory where the file is saved
// 3. Compile the code using the command: javac QuickSort.java
// 4. Run the compiled code using the command: java QuickSort
