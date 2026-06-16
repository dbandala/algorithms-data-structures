// Find if two lists share a common element using a hash set for O(1) lookup
// Time complexity:  O(n + m)
// Space complexity: O(n)

#include <iostream>
#include <vector>
#include <unordered_set>

bool item_in_common(const std::vector<int>& list1, const std::vector<int>& list2) {
    std::unordered_set<int> hash_set;
    for (int item : list1)
        hash_set.insert(item);
    for (int item : list2) {
        if (hash_set.count(item))
            return true;
    }
    return false;
}

int main() {
    std::cout << std::boolalpha;

    std::vector<int> list1 = {1, 3, 5};
    std::vector<int> list2 = {2, 4, 5};
    std::cout << item_in_common(list1, list2) << "\n";  // true

    std::vector<int> list3 = {1, 2, 3};
    std::vector<int> list4 = {4, 5, 6};
    std::cout << item_in_common(list3, list4) << "\n";  // false
    return 0;
}
