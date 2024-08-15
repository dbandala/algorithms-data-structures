class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []
            return True
        return False
    
    def add_edge(self, vertex1, vertex2):
        if vertex1 in self.adj_list.keys() and vertex2 in self.adj_list.keys():
            self.adj_list[vertex1].append(vertex2)
            self.adj_list[vertex2].append(vertex1)
            return True
        return False
    
    def remove_edge(self, v1, v2):
        if v1 not in self.adj_list or v2 not in self.adj_list:
            return False
        # self.adj_list[v1] = [vertex for vertex in self.adj_list[v1] if vertex != v2]
        # self.adj_list[v2] = [vertex for vertex in self.adj_list[v2] if vertex != v1]
        try:
            self.adj_list[v1].remove(v2) # remove() raises ValueError if the value is not found - because is a list
            self.adj_list[v2].remove(v1)
            return True
        except ValueError:
            return False
        
    def remove_vertex(self, vertex):
        if vertex not in self.adj_list:
            return False
        for v in self.adj_list[vertex]:
            try:
                self.adj_list[v].remove(vertex)
            except ValueError:
                pass
        self.adj_list.pop(vertex)
        return True



# Test cases
graph = Graph()
graph.add_vertex(1)
graph.add_vertex(2)
graph.add_vertex(3)
graph.add_vertex('A')
print(graph.adj_list) # {1: [], 2: [], 3: []}

graph.add_edge(1, 2)
graph.add_edge(1, 3)
graph.add_edge(2, 3)
graph.add_edge(2, 'A')
print(graph.adj_list) # {1: [2, 3], 2: [1, 3, 'A'], 3: [1, 2], 'A': [2]}

graph.remove_edge(2, 3)
print(graph.adj_list) # {1: [2, 3], 2: [1, 'A'], 3: [1], 'A': [2]}

graph.remove_vertex(2)
print(graph.adj_list) # {1: [3], 3: [1]}