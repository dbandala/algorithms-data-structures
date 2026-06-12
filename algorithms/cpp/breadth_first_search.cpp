// Breadth-First Search (BFS) on an unweighted undirected graph
// Uses adjacency list representation and a queue
// Time complexity:  O(V + E)
// Space complexity: O(V)

#include <iostream>
#include <string>
#include <vector>
#include <queue>
#include <unordered_map>
#include <unordered_set>

class Graph {
public:
    std::unordered_map<std::string, std::vector<std::string>> adj;

    void add_edge(const std::string& u, const std::string& v) {
        adj[u].push_back(v);
        adj[v].push_back(u);  // undirected
    }

    std::vector<std::string> bfs(const std::string& start) {
        std::vector<std::string> visited_order;
        std::unordered_set<std::string> visited;
        std::queue<std::string> q;

        visited.insert(start);
        q.push(start);

        while (!q.empty()) {
            std::string node = q.front();
            q.pop();
            visited_order.push_back(node);

            for (const std::string& neighbor : adj[node]) {
                if (!visited.count(neighbor)) {
                    visited.insert(neighbor);
                    q.push(neighbor);
                }
            }
        }
        return visited_order;
    }
};

int main() {
    Graph g;
    g.add_edge("A", "B");
    g.add_edge("A", "C");
    g.add_edge("B", "D");
    g.add_edge("B", "E");
    g.add_edge("C", "F");

    std::cout << "BFS from A: ";
    for (const std::string& node : g.bfs("A"))
        std::cout << node << " ";
    std::cout << "\n";  // A B C D E F (BFS order)
    return 0;
}
