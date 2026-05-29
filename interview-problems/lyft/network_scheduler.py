# Network scheduler (minimum worker assignment)
# Reported Lyft onsite: assign interval jobs to the fewest workers possible.
#
# Each job [start, duration] occupies half-open interval [start, start + duration).
# A job ending at time x does NOT overlap one starting at x.
#
# Interview flow:
#   1. Clarify half-open intervals and deterministic worker IDs (0-based).
#   2. Sort by start time (tie-break: original index).
#   3. Two min-heaps: busy workers by end time, free workers by ID.
#   4. Greedy reuse of smallest free worker is optimal (exchange argument).
#
# O(n log n) time, O(n) space for n jobs.

from __future__ import annotations

import heapq
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    """A unit of work with a fixed start time and duration."""

    start: int
    duration: int

    @property
    def end(self) -> int:
        """Exclusive end of the half-open interval [start, end)."""
        return self.start + self.duration


class NetworkScheduler:
    """
    Assign interval jobs to workers with no overlap per worker.

    Uses the minimum number of workers and returns worker IDs in input order.
    When multiple workers are free, the smallest ID is reused first.
    """

    def assign_workers(self, jobs: list[list[int]]) -> list[int]:
        """
        Assign each job to a worker and return worker IDs in original order.

        Args:
            jobs: Each entry is [start, duration] for half-open [start, start + duration).

        Returns:
            Worker ID (0-based) for each job, same length and order as jobs.
        """
        if not jobs:
            return []

        indexed_jobs = [
            (Job(start, duration), index)
            for index, (start, duration) in enumerate(jobs)
        ]
        indexed_jobs.sort(key=lambda item: (item[0].start, item[1]))

        assignments = [0] * len(jobs)
        busy_workers: list[tuple[int, int]] = []  # (end_time, worker_id)
        free_workers: list[int] = []  # min-heap of reusable worker IDs
        next_worker_id = 0

        for job, original_index in indexed_jobs:
            self._release_finished_workers(busy_workers, free_workers, job.start)

            if free_workers:
                worker_id = heapq.heappop(free_workers)
            else:
                worker_id = next_worker_id
                next_worker_id += 1

            assignments[original_index] = worker_id
            heapq.heappush(busy_workers, (job.end, worker_id))

        return assignments

    def min_workers_needed(self, jobs: list[list[int]]) -> int:
        """
        Return the minimum number of workers required for the job set.

        Equivalent to max concurrent overlap (meeting rooms II), but computed
        via the same greedy assignment for consistency.
        """
        if not jobs:
            return 0
        worker_ids = self.assign_workers(jobs)
        return max(worker_ids) + 1

    @staticmethod
    def _release_finished_workers(
        busy_workers: list[tuple[int, int]],
        free_workers: list[int],
        current_start: int,
    ) -> None:
        """
        Move workers whose last job ended at or before current_start to the free pool.

        Half-open intervals allow end == current_start (worker is available).
        """
        while busy_workers and busy_workers[0][0] <= current_start:
            _, worker_id = heapq.heappop(busy_workers)
            heapq.heappush(free_workers, worker_id)


if __name__ == "__main__":
    scheduler = NetworkScheduler()

    assert scheduler.assign_workers([[0, 5], [1, 2], [6, 1]]) == [0, 1, 0]
    assert scheduler.assign_workers([[0, 3], [3, 2], [5, 1]]) == [0, 0, 0]
    assert scheduler.assign_workers([[2, 4], [2, 1], [3, 2], [7, 1]]) == [0, 1, 1, 0]
    assert scheduler.assign_workers([]) == []
    assert scheduler.assign_workers([[1, 0], [1, 0], [1, 1]]) == [0, 0, 0]

    assert scheduler.min_workers_needed([[0, 5], [1, 2], [6, 1]]) == 2
    assert scheduler.min_workers_needed([[0, 3], [3, 2], [5, 1]]) == 1

    print("all network scheduler tests passed")
