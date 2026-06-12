// Depth-First Search (DFS) on an unweighted undirected graph
// Uses adjacency list representation with recursive traversal
// Time complexity:  O(V + E)
// Space complexity: O(V) for the visited set + O(h) call stack

#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>

class Graph {
private:
    void dfs_helper(const std::string& node,
                    std::unordered_set<std::string>& visited,
                    std::vector<std::string>& order) {
        visited.insert(node);
        order.push_back(node);
        for (const std::string& neighbor : adj.at(node)) {
            if (!visited.count(neighbor))
                dfs_helper(neighbor, visited, order);
        }
    }

public:
    std::unordered_map<std::string, std::vector<std::string>> adj;

    void add_edge(const std::string& u, const std::string& v) {
        adj[u].push_back(v);
        adj[v].push_back(u);  // undirected
    }

    std::vector<std::string> dfs(const std::string& start) {
        std::vector<std::string> order;
        std::unordered_set<std::string> visited;
        dfs_helper(start, visited, order);
        return order;
    }
};

int main() {
    Graph g;
    g.add_edge("A", "B");
    g.add_edge("A", "C");
    g.add_edge("B", "D");
    g.add_edge("B", "E");
    g.add_edge("C", "F");

    std::cout << "DFS from A: ";
    for (const std::string& node : g.dfs("A"))
        std::cout << node << " ";
    std::cout << "\n";  // A B/C D/E ... (DFS order)
    return 0;
}
