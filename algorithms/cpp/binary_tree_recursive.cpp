// Binary Search Tree with iterative insert/contains and recursive variants
// Supports: insert, contains, r_contains, r_insert, delete_node

#include <iostream>

struct Node {
    int value;
    Node* left;
    Node* right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

class BinaryTree {
private:
    Node* root;

    bool _r_contains(Node* node, int value) {
        if (node == nullptr) return false;
        if (value < node->value) return _r_contains(node->left, value);
        if (value > node->value) return _r_contains(node->right, value);
        return true;
    }

    Node* _r_insert(Node* node, int value) {
        if (node == nullptr) return new Node(value);
        if (value < node->value)
            node->left = _r_insert(node->left, value);
        else if (value > node->value)
            node->right = _r_insert(node->right, value);
        return node;
    }

    int min_value(Node* node) {
        if (node->left == nullptr) return node->value;
        return min_value(node->left);
    }

    Node* _delete_node(Node* node, int value) {
        if (node == nullptr) return nullptr;
        if (value < node->value) {
            node->left = _delete_node(node->left, value);
        } else if (value > node->value) {
            node->right = _delete_node(node->right, value);
        } else {
            if (node->left == nullptr && node->right == nullptr) {
                delete node;
                return nullptr;
            } else if (node->left == nullptr) {
                Node* temp = node->right;
                delete node;
                return temp;
            } else if (node->right == nullptr) {
                Node* temp = node->left;
                delete node;
                return temp;
            } else {
                int sub_tree_min = min_value(node->right);
                node->value = sub_tree_min;
                node->right = _delete_node(node->right, sub_tree_min);
            }
        }
        return node;
    }

public:
    BinaryTree() : root(nullptr) {}

    bool insert(int value) {
        Node* new_node = new Node(value);
        if (root == nullptr) {
            root = new_node;
            return true;
        }
        Node* current = root;
        while (true) {
            if (value < current->value) {
                if (current->left == nullptr) { current->left = new_node; return true; }
                current = current->left;
            } else if (value > current->value) {
                if (current->right == nullptr) { current->right = new_node; return true; }
                current = current->right;
            } else {
                delete new_node;
                return false;  // duplicate
            }
        }
    }

    bool contains(int value) {
        Node* current = root;
        while (current) {
            if (value < current->value)      current = current->left;
            else if (value > current->value) current = current->right;
            else                             return true;
        }
        return false;
    }

    bool r_contains(int value) {
        return _r_contains(root, value);
    }

    void r_insert(int value) {
        if (root == nullptr) { root = new Node(value); return; }
        _r_insert(root, value);
    }

    void delete_node(int value) {
        root = _delete_node(root, value);
    }
};

int main() {
    std::cout << std::boolalpha;

    BinaryTree tree;
    tree.insert(10);
    tree.insert(5);
    tree.insert(15);
    tree.insert(2);
    tree.insert(7);

    std::cout << "contains(7):    " << tree.contains(7)    << "\n";  // true
    std::cout << "contains(9):    " << tree.contains(9)    << "\n";  // false
    std::cout << "r_contains(5):  " << tree.r_contains(5)  << "\n";  // true
    std::cout << "r_contains(15): " << tree.r_contains(15) << "\n";  // true

    tree.delete_node(5);
    std::cout << "after delete(5), contains(5): " << tree.contains(5) << "\n";  // false
    std::cout << "after delete(5), contains(7): " << tree.contains(7) << "\n";  // true

    BinaryTree tree2;
    tree2.r_insert(10);
    tree2.r_insert(5);
    tree2.r_insert(15);
    std::cout << "r_insert tree, contains(15): " << tree2.contains(15) << "\n";  // true
    std::cout << "r_insert tree, contains(1):  " << tree2.contains(1)  << "\n";  // false
    return 0;
}
