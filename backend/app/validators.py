from typing import Tuple, Dict, Any, List

def require_json_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
    """
    Validates that the provided dictionary contains all required fields.
    Returns (True, "") if all fields are present, (False, error_message) otherwise. 
    """
    missing = [field for field in required_fields if not data or field not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""


def sanitize_str(value: str, max_len: int = 500) -> str:
    """
    Basic sanitizer and length trimmer.
    """
    if not isinstance(value, str):
        value = str(value)
    return value[:max_len].strip()


def parse_pagination(args: Dict[str, str], default_per_page: int = 20, max_per_page: int = 100) -> Tuple[int, int]:
    """
    Extracts and standardizes pagination query params.
    Returns (page, per_page) safe integers.
    """
    try:
        page = int(args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
        
    try:
        per_page = int(args.get('per_page', default_per_page))
        if per_page < 1:
            per_page = default_per_page
        elif per_page > max_per_page:
            per_page = max_per_page
    except (ValueError, TypeError):
        per_page = default_per_page
        
    return page, per_page
