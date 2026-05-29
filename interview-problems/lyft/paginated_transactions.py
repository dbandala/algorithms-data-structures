# Cursor-based transaction pagination
# Reported: Jul 2025 NYC laptop round (“pagination issue”); PracHub Lyft onsite.
#
# Sort: created_at DESC, tie-break txn_id ASC.
# Opaque cursor (encode/decode) — client must not parse it.
# Stable pages: new inserts while paging must not cause duplicates or skips.

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Transaction:
    """A single financial transaction."""

    txn_id: int
    user_id: int
    amount: float
    created_at: int  # epoch seconds


def encode_cursor(created_at: int, txn_id: int) -> str:
    """
    Build an opaque cursor from the last row on a page.

    Clients pass this string back unchanged on the next request.
    """
    payload = json.dumps({"t": created_at, "id": txn_id}, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: str) -> tuple[int, int]:
    """
    Recover (created_at, txn_id) from an opaque cursor.

    Raises ValueError if the cursor is missing, malformed, or tampered with.
    """
    if not cursor:
        raise ValueError("cursor must be a non-empty string")
    try:
        raw = base64.urlsafe_b64decode(cursor.encode())
        data = json.loads(raw.decode())
        return int(data["t"]), int(data["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid cursor") from exc


def _sort_key(txn: Transaction) -> tuple[int, int]:
    """Sort newest first; break ties by smaller txn_id first."""
    return (-txn.created_at, txn.txn_id)


def _is_strictly_after(txn: Transaction, cursor_at: int, cursor_txn_id: int) -> bool:
    """
    True when txn sorts after (created_at DESC, txn_id ASC) the cursor position.

    The cursor marks the last row the client already received; the next page
    must exclude that row and everything above it in the sort order.
    """
    if txn.created_at < cursor_at:
        return True
    if txn.created_at == cursor_at and txn.txn_id > cursor_txn_id:
        return True
    return False


class PaginatedTransactions:
    """In-memory transaction store with cursor- and offset-based pagination."""

    def __init__(self, transactions: Optional[list[Transaction]] = None) -> None:
        self._txns: list[Transaction] = list(transactions or [])

    def add_transaction(self, transaction: Transaction) -> None:
        """Append a transaction (simulates live inserts during paging)."""
        self._txns.append(transaction)

    def _transactions_for_user(self, user_id: Optional[int]) -> list[Transaction]:
        """Return all transactions for a user, sorted for pagination."""
        if user_id is None:
            return []
        user_txns = [t for t in self._txns if t.user_id == user_id]
        user_txns.sort(key=_sort_key)
        return user_txns

    def get_transactions(
        self,
        user_id: Optional[int],
        cursor: Optional[str],
        limit: int,
    ) -> tuple[list[Transaction], Optional[str]]:
        """
        Return the next page of transactions and an opaque next_cursor.

        Args:
            user_id: Owner of the transactions; None yields an empty page.
            cursor: Opaque token from a previous response, or None for the first page.
            limit: Maximum rows to return (0 yields an empty page).

        Returns:
            (page, next_cursor) where next_cursor is None on the last page.
        """
        if limit < 0:
            raise ValueError("limit must be non-negative")
        if user_id is None:
            return [], None
        if limit == 0:
            return [], cursor

        candidates = self._transactions_for_user(user_id)

        if cursor is not None:
            cursor_at, cursor_txn_id = decode_cursor(cursor)
            candidates = [
                t
                for t in candidates
                if _is_strictly_after(t, cursor_at, cursor_txn_id)
            ]

        page = candidates[:limit]
        if len(page) < limit:
            return page, None

        last = page[-1]
        return page, encode_cursor(last.created_at, last.txn_id)

    def get_transactions_offset(
        self,
        user_id: Optional[int],
        offset: int,
        limit: int,
    ) -> tuple[list[Transaction], int]:
        """
        Offset-based pagination with total count (Part 2).

        Less stable than cursor mode when rows are inserted concurrently, but
        supports random access to pages and a total for UI page indicators.

        Returns:
            (page, total_count) where total_count is the number of matching rows.
        """
        if offset < 0 or limit < 0:
            raise ValueError("offset and limit must be non-negative")
        if user_id is None:
            return [], 0
        if limit == 0:
            return [], len(self._transactions_for_user(user_id))

        all_for_user = self._transactions_for_user(user_id)
        total = len(all_for_user)
        page = all_for_user[offset : offset + limit]
        return page, total


def _run_examples() -> None:
    """Smoke-test cursor stability and tie-breaking."""
    store = PaginatedTransactions(
        [
            Transaction(100, 1, 10.0, 1000),
            Transaction(200, 1, 20.0, 1000),
            Transaction(50, 1, 5.0, 999),
            Transaction(1, 2, 1.0, 500),
        ]
    )

    page1, c1 = store.get_transactions(user_id=1, cursor=None, limit=2)
    assert [t.txn_id for t in page1] == [100, 200]
    assert c1 is not None

    store.add_transaction(Transaction(150, 1, 15.0, 1000))

    page2, c2 = store.get_transactions(user_id=1, cursor=c1, limit=2)
    assert [t.txn_id for t in page2] == [50]
    assert c2 is None

    page_empty, _ = store.get_transactions(user_id=None, cursor=None, limit=10)
    assert page_empty == []

    zero, kept = store.get_transactions(user_id=1, cursor=None, limit=0)
    assert zero == [] and kept is None

    offset_page, total = store.get_transactions_offset(user_id=1, offset=0, limit=2)
    assert [t.txn_id for t in offset_page] == [100, 150]
    assert total == 4


if __name__ == "__main__":
    _run_examples()
    print("paginated_transactions: all examples passed")
