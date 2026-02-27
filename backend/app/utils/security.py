# app/utils/security.py

def escape_like_term(term, escape_char='\\'):
    """
    Escapes characters that have special meaning in SQL LIKE clauses.

    Args:
        term (str): The search term to escape.
        escape_char (str): The escape character to use (default: '\').

    Returns:
        str: The escaped search term.
    """
    if not term:
        return term

    # Escape the escape character itself first
    term = term.replace(escape_char, escape_char + escape_char)

    # Escape the wildcard characters
    term = term.replace('%', escape_char + '%')
    term = term.replace('_', escape_char + '_')

    return term
