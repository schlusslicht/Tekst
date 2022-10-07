import re
import unicodedata as ucdata


def safe_name(
    string: str,
    min_len: int = 0,
    max_len: int = 32,
    delim: str = "_",
) -> str:
    """Creates a safe name (e.g. for use as an identifier) from the input string.

    Removes diacritics, lowercases, replaces spaces with underscores and
    applies the defined length constraints. If min_len is set to >0 and fails,
    the string will be left-justified and filled with underscores until min_len is met.
    """

    # support byte strings
    if isinstance(string, bytes):
        string = string.decode()

    string = remove_diacritics(string)

    # lowercase and delimit using underscores
    string = re.sub(r"[^a-z0-9]+", delim, string.lower()).strip(delim)

    # apply length constraints
    if min_len > 0 and len(string) < min_len:
        string = string.ljust(min_len, delim)
    elif len(string) > max_len:
        string = string[:max_len].strip(delim)

    return string


def remove_diacritics(string: str) -> str:
    """Removes diacritics from the input string."""

    return "".join(
        c for c in ucdata.normalize("NFD", string) if ucdata.category(c) != "Mn"
    )


def snake_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )
