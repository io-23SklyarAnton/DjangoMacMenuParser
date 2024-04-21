def clear_string(string: str) -> str:
    return string.replace('\n', '').replace('\r', '').replace('\t', '').strip()
