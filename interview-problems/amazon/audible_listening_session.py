# Implement a function to determine if a user's listening session is continuous, given a series of start and end timestamps.

def is_continuous_session(timestamps):
    if not timestamps:
        return False

    # Sort timestamps by start time
    timestamps.sort(key=lambda x: x[0])

    # Check for continuity
    for i in range(1, len(timestamps)):
        if timestamps[i][0] > timestamps[i - 1][1]:
            return False

    return True