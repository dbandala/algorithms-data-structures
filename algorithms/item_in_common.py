def item_in_common(list1, list2):
    # Create a hash table
    hash_table = {}
    # Loop through the first list
    for item in list1:
        # Add each item to the hash table
        hash_table[item] = True
    # Loop through the second list
    for item in list2:
        # If the item is in the hash table
        if hash_table.get(item):
            # Return True
            return True
    # Return False
    return False