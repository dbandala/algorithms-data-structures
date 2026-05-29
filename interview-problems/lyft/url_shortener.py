# URL Shortener
# Problema
# “Diseña un sistema para acortar URLs.”

# Ejemplo:
# * Input: "https://www.google.com"
# * Output: "https://ly.ft/1234567890"

# Implementar algo como:
# def shorten_url(url: str) -> str:
#     pass

# Nivel Senior
# * Complejidad temporal
# * Memory efficiency
# * Race conditions
# * Distributed systems thinking
# * Redis discussion
# * Horizontal scaling

# Tecnologías que puedes mencionar
# * Apache Kafka
# * Amazon Web Services SQS
# * Pub/Sub
# * Consumer groups

# Interview approach: monotonic id + base62 encoding.
# - shorten / expand: O(1) average with hash maps
# - same long URL → same short URL (dedup)
# Production: counter from DB/Redis INCR, base62 in app; shard by hash prefix at scale.


_BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _to_base62(num: int) -> str:
    """Encode a non-negative integer as a base62 string."""
    if num == 0:
        return _BASE62[0]
    chars = []
    while num:
        num, remainder = divmod(num, 62)
        chars.append(_BASE62[remainder])
    return "".join(reversed(chars))


class UrlShortener(object):
    """In-memory URL shortener with shorten and expand."""

    def __init__(self, base_url: str = "https://ly.ft/"):
        """
        Initialize the shortener.

        :type base_url: str
        """
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self._url_to_code = {}
        self._code_to_url = {}
        self._next_id = 0

    def shorten_url(self, url: str) -> str:
        """
        Return a short URL for the given long URL. Reuses an existing code
        when the same long URL is shortened again.

        :type url: str
        :rtype: str
        """
        if url in self._url_to_code:
            return self.base_url + self._url_to_code[url]

        self._next_id += 1
        code = _to_base62(self._next_id)
        self._url_to_code[url] = code
        self._code_to_url[code] = url
        return self.base_url + code

    def expand_url(self, short_url: str) -> str:
        """
        Resolve a short URL (full form or code only) back to the original URL.

        :type short_url: str
        :rtype: str
        :raises KeyError: if the code is unknown
        """
        code = self._extract_code(short_url)
        return self._code_to_url[code]

    def _extract_code(self, short_url: str) -> str:
        """Pull the short code from a full short URL or return it as-is."""
        if short_url.startswith(self.base_url):
            return short_url[len(self.base_url) :]
        return short_url.rstrip("/").split("/")[-1]


if __name__ == "__main__":
    shortener = UrlShortener()
    long_url = "https://www.google.com"
    short = shortener.shorten_url(long_url)
    assert short.startswith("https://ly.ft/")
    assert shortener.expand_url(short) == long_url
    assert shortener.shorten_url(long_url) == short  # dedup
    print(short, "->", shortener.expand_url(short))
