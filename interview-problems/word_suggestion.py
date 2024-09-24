# Etsy interview question

vocab = [
    "apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew",
    "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry",
    "strawberry", "tangerine", "ugli", "vanilla", "watermelon", "xigua", "yam", "zucchini",
    "apricot", "blackberry", "cantaloupe", "dragonfruit", "elderflower", "feijoa", "guava",
    "huckleberry", "jackfruit", "kumquat", "lime", "mulberry", "olive", "peach", "plum",
    "quinoa", "rambutan", "starfruit", "tomato", "ugni", "voavanga", "wolfberry", "ximenia",
    "yuzu", "ziziphus", "avocado", "bilberry", "clementine", "durian", "eggplant", "fig",
    "grapefruit", "honeyberry"
]

def autocomplete(prefix):
    # approach: use trie to store the vocab and search for the prefix
    # and return the words that start with the prefix
    trie = {}
    for word in vocab:
        node = trie
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node['*'] = True

    node = trie
    for char in prefix:
        if char not in node:
            return []
        node = node[char]

    def _dfs(node, prefix):
        if '*' in node:
            return [prefix]
        words = []
        for char in node:
            if char!='*':
                words += _dfs(node[char], prefix+char)
        return words

    return _dfs(node, prefix)

print(autocomplete("a")) # ['apple', 'apricot', 'avocado']