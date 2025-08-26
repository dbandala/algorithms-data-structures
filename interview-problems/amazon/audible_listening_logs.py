# Given a massive log file of user listening history, design an algorithm to find the top K most listened-to audiobooks.

class Solution(object):
    def mostListenedAudiobooks(self, listening_history: list, k: int):
        """
          listening_history: list []
          k: int
          returns top k most listened audiobook
          returns list []
        """
        list_counter = {}
        for lh in listening_history:
            if lh in list_counter:
                list_counter[lh] += 1
            else:
                list_counter[lh] = 1


        # Find the top k most listened audiobooks
        top_k = sorted(list_counter.items(), key=lambda x: x[1], reverse=True)[:k]
        return [book for book, count in top_k]
    

# Test cases
sol = Solution()
print(sol.mostListenedAudiobooks(["book1", "book2", "book1", "book3", "book2", "book1"], 2)) # ["book1", "book2"]
print(sol.mostListenedAudiobooks(["bookA", "bookB", "bookC", "bookA", "bookB"], 1)) # ["bookA"]
