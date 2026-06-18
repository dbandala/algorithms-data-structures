// Check if two binary trees are structurally identical with the same node values
// Time complexity:  O(n)
// Space complexity: O(h) where h is the height of the tree

#include <iostream>

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v = 0, TreeNode* l = nullptr, TreeNode* r = nullptr)
        : val(v), left(l), right(r) {}
};

bool isSameTree(TreeNode* p, TreeNode* q) {
    if (p == nullptr && q == nullptr) return true;
    if (p == nullptr || q == nullptr) return false;
    if (p->val != q->val) return false;
    return isSameTree(p->left, q->left) && isSameTree(p->right, q->right);
}

int main() {
    std::cout << std::boolalpha;

    // Test case 1: same trees [1,2,3]
    TreeNode* p1 = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    TreeNode* q1 = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    std::cout << isSameTree(p1, q1) << "\n";  // true

    // Test case 2: different structure [1,2] vs [1,null,2]
    TreeNode* p2 = new TreeNode(1, new TreeNode(2), nullptr);
    TreeNode* q2 = new TreeNode(1, nullptr, new TreeNode(2));
    std::cout << isSameTree(p2, q2) << "\n";  // false

    // Test case 3: different values [1,2,3] vs [1,2,4]
    TreeNode* p3 = new TreeNode(1, new TreeNode(2), new TreeNode(3));
    TreeNode* q3 = new TreeNode(1, new TreeNode(2), new TreeNode(4));
    std::cout << isSameTree(p3, q3) << "\n";  // false
    return 0;
}
