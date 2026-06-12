// Dijkstra's algorithm - shortest path from source to a single destination
// Stops early once the destination vertex is settled
// Undirected weighted graph using adjacency matrix
// Time complexity:  O(V^2) worst case, often faster with early exit
// Space complexity: O(V)

#include <iostream>
#include <vector>
#include <string>
#include <limits>
#include <algorithm>

class Graph {
public:
    int size;
    std::vector<std::vector<double>> adj_matrix;
    std::vector<std::string> vertex_data;

    Graph(int size)
        : size(size),
          adj_matrix(size, std::vector<double>(size, 0.0)),
          vertex_data(size, "") {}

    void add_edge(int u, int v, double weight) {
        if (u >= 0 && u < size && v >= 0 && v < size) {
            adj_matrix[u][v] = weight;
            adj_matrix[v][u] = weight;  // undirected
        }
    }

    void add_vertex_data(int vertex, const std::string& data) {
        if (vertex >= 0 && vertex < size)
            vertex_data[vertex] = data;
    }

    // Returns distance from start to end_vertex_data; stops as soon as end is settled
    double dijkstra(const std::string& start_vertex_data,
                    const std::string& end_vertex_data) {
        int start = static_cast<int>(
            std::find(vertex_data.begin(), vertex_data.end(), start_vertex_data)
            - vertex_data.begin());
        int end = static_cast<int>(
            std::find(vertex_data.begin(), vertex_data.end(), end_vertex_data)
            - vertex_data.begin());

        std::vector<double> distances(size, std::numeric_limits<double>::infinity());
        std::vector<bool> visited(size, false);
        distances[start] = 0.0;

        for (int iter = 0; iter < size; ++iter) {
            double min_dist = std::numeric_limits<double>::infinity();
            int u = -1;
            for (int i = 0; i < size; ++i) {
                if (!visited[i] && distances[i] < min_dist) {
                    min_dist = distances[i];
                    u = i;
                }
            }
            if (u == -1) break;
            if (u == end) break;  // destination settled — early exit

            visited[u] = true;

            for (int v = 0; v < size; ++v) {
                if (adj_matrix[u][v] != 0.0 && !visited[v]) {
                    double alt = distances[u] + adj_matrix[u][v];
                    if (alt < distances[v])
                        distances[v] = alt;
                }
            }
        }
        return distances[end];
    }
};

int main() {
    Graph g(7);
    g.add_vertex_data(0, "A");
    g.add_vertex_data(1, "B");
    g.add_vertex_data(2, "C");
    g.add_vertex_data(3, "D");
    g.add_vertex_data(4, "E");
    g.add_vertex_data(5, "F");
    g.add_vertex_data(6, "G");

    g.add_edge(3, 0, 4);  // D - A, weight 4
    g.add_edge(3, 4, 2);  // D - E, weight 2
    g.add_edge(0, 2, 3);  // A - C, weight 3
    g.add_edge(0, 4, 4);  // A - E, weight 4
    g.add_edge(4, 2, 4);  // E - C, weight 4
    g.add_edge(4, 6, 5);  // E - G, weight 5
    g.add_edge(2, 5, 5);  // C - F, weight 5
    g.add_edge(2, 1, 2);  // C - B, weight 2
    g.add_edge(1, 5, 2);  // B - F, weight 2
    g.add_edge(6, 5, 5);  // G - F, weight 5

    std::cout << "\nDijkstra's Algorithm starting from vertex D:\n";
    std::vector<std::string> destinations = {"A", "B", "C", "D", "E", "F", "G"};
    for (const std::string& dest : destinations) {
        double d = g.dijkstra("D", dest);
        std::cout << "Distance D -> " << dest << ": " << d << "\n";
    }

    return 0;
}
