# Lyft Laptop Interview
# This question simulates solving a problem in a real world setting, separate from the whiteboard problems you'll solve in the rest of your interview. Since we're simulating the real world:

# Correctness (50%) - Your code should pass the sample test cases and other test cases you can think of. Handle edge cases sensibly. Don't worry about thread-safety or rogue input that doesn't adhere to the problem spec.
# Clean Code (35%) - Your code should be split up into multiple classes or functions when relevant. It doesn't have to be in multiple files. It should have comments where relevant, but don't add comments just for the sake of commenting.
# Performance (15%) - If you can make your solution's time and space complexity better, without sacrificing correctness, please do so!
# Remember, if you get really stuck, try and make progress however you can. Focus on simple cases, reduce the problem to more simpler components, and ask your interviewer for how to prioritize your time.

# Here's the problem:

# In-Memory Key-Value Database
# Overview
# You are to build a data structure for storing integers. You will not persist the database to disk, you will store the data in memory.

# For simplicity's sake, instead of dealing with multiple clients and communicating over the network, your program will receive commands via stdin, and should write appropriate responses to stdout. Each line of the input will be a command (specified below) followed by a specific number of arguments depending on the command.

# For example:
# Your database should accept the following commands.

# SET name value

# Set the variable name to the value value. Neither variable names nor values will contain spaces.

# GET name

# Print out the value of the variable name, or NULL if that variable is not set.

# UNSET name

# Unset the variable name, making it just like that variable was never set.

# NUMWITHVALUE value

# Print out the number of variables that are currently set to value. If no variables equal that value, print 0.

# END

# Exit the program. Your program will always receive this as its last command.

# Once your database accepts the above commands and is tested and works, implement commands below.

# BEGIN

# Open a new transaction block. Transaction blocks can be nested (BEGIN can be issued inside of an existing block) but you should get non-nested transactions working first before starting on nested. A GET within a transaction returns the latest value by any command. Any data command that is run outside of a transaction block should commit immediately.

# ROLLBACK

# Undo all of the commands issued in the most recent transaction block, and close the block. Print nothing if successful, or print NO TRANSACTION if no transaction is in progress.

# COMMIT

# Close all open transaction blocks, permanently applying the changes made in them. Print nothing if successful, or print NO TRANSACTION if no transaction is in progress.

# Your output should contain the output of the GET and NUMWITHVALUE commands. GET will print out the value of the specified key, or NULL. NUMWITHVALUE will return the number of keys which have the specified value.



"""
In-Memory Key-Value Database
Supports: SET, GET, UNSET, NUMWITHVALUE, BEGIN, ROLLBACK, COMMIT, END
"""
import sys

# Sentinel to distinguish "unset" from any real value inside a transaction snapshot
_UNSET = object()


class KeyValueDB:
    def __init__(self):
        self.store = {}          # name -> value (current committed/live state)
        self.value_counts = {}   # value -> count of keys holding that value
        # Each entry in the stack is a dict of {name: old_value_or_UNSET}
        # representing what we'd need to restore on ROLLBACK.
        self.tx_stack = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_for_rollback(self, name):
        """Save the pre-change value of `name` in the current transaction
        frame, but only if we haven't already recorded it (first-write wins,
        so we always keep the value that existed when the tx opened)."""
        if not self.tx_stack:
            return
        frame = self.tx_stack[-1]
        if name not in frame:
            frame[name] = self.store.get(name, _UNSET)

    def _inc_count(self, value):
        self.value_counts[value] = self.value_counts.get(value, 0) + 1

    def _dec_count(self, value):
        count = self.value_counts.get(value, 0) - 1
        if count <= 0:
            self.value_counts.pop(value, None)
        else:
            self.value_counts[value] = count

    # ------------------------------------------------------------------
    # Core commands
    # ------------------------------------------------------------------

    def set(self, name, value):
        self._record_for_rollback(name)
        old = self.store.get(name)
        if old is not None:
            self._dec_count(old)
        self.store[name] = value
        self._inc_count(value)

    def get(self, name):
        return self.store.get(name, "NULL")

    def unset(self, name):
        if name not in self.store:
            return
        self._record_for_rollback(name)
        self._dec_count(self.store.pop(name))

    def num_with_value(self, value):
        return self.value_counts.get(value, 0)

    # ------------------------------------------------------------------
    # Transaction commands
    # ------------------------------------------------------------------

    def begin(self):
        self.tx_stack.append({})

    def rollback(self):
        if not self.tx_stack:
            return "NO TRANSACTION"
        frame = self.tx_stack.pop()
        # Restore each key to its pre-transaction value in reverse order of
        # recording so that count bookkeeping stays consistent.
        for name, old_value in frame.items():
            current = self.store.get(name)
            if current is not None:
                self._dec_count(current)
            if old_value is _UNSET:
                self.store.pop(name, None)
            else:
                self.store[name] = old_value
                self._inc_count(old_value)
        return None  # success → print nothing

    def commit(self):
        if not self.tx_stack:
            return "NO TRANSACTION"
        # Discard all rollback info — current state is now permanent.
        self.tx_stack.clear()
        return None  # success → print nothing


# ------------------------------------------------------------------
# Command dispatcher
# ------------------------------------------------------------------

def run(input_stream=sys.stdin, output_stream=sys.stdout):
    db = KeyValueDB()

    for raw_line in input_stream:
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        cmd = parts[0].upper()

        if cmd == "SET":
            db.set(parts[1], parts[2])

        elif cmd == "GET":
            print(db.get(parts[1]), file=output_stream)

        elif cmd == "UNSET":
            db.unset(parts[1])

        elif cmd == "NUMWITHVALUE":
            print(db.num_with_value(parts[1]), file=output_stream)

        elif cmd == "BEGIN":
            db.begin()

        elif cmd == "ROLLBACK":
            result = db.rollback()
            if result:
                print(result, file=output_stream)

        elif cmd == "COMMIT":
            result = db.commit()
            if result:
                print(result, file=output_stream)

        elif cmd == "END":
            break


if __name__ == "__main__":
    run()