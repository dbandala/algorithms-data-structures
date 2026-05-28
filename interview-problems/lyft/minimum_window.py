# We are given a corpus and a target sequence. We want to find the first minimal (shortest) substring in the corpus, which contains all of the characters from the target sequence. Order does not matter but characters in the target sequence may appear multiple times. Assume a valid string input for the target and corpus.
'''
    min_substring("abc", "aaaaaabbcccccc") == "abbc"
    min_substring("abc", "aabbccabc") == "cab"
'''


def min_substring(target, corpus): # O(n+m)
    """
    type target: str
    type corpus str
    rtype str
    """
    needed = {}
    have = {}

    for c in target:
        needed[c] = needed.get(c, 0) + 1

    needed_count = len(needed)

    left = 0
    satisfied_count = 0
    best = (float('inf'), "")
    for right in range(len(corpus)): # O(n)
        char = corpus[right]

        have[char] = have.get(char, 0) + 1

        # verify that char satisfies needed counter
        if char in needed and have[char]==needed[char]:
            satisfied_count += 1

        # shorten
        while left<right and satisfied_count==needed_count: # O(m)
            current_length = right-left+1
            if current_length<best[0]:
                best = (current_length, corpus[left:right+1])
            
            # shorten by left
            cr = corpus[left]
            have[cr] -= 1
            if cr in needed and have[cr]<needed[cr]:
                satisfied_count -= 1
            
            left += 1



    return best[1]


    
print(min_substring("abbc", "abbbbbccccca"))
print(min_substring("aab", "abbbbbbbbba"))



# Your previous Plain Text content is preserved below:

# Pad for Daniel Bandala - Sr Software Engineer, Luxury