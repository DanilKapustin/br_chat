def first_n_words(string: str, n: int) -> str:
    """Return first N words of a string"""
    return " ".join(string.split()[:n])
