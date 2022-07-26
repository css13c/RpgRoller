def try_parse_int(val: str):
    try:
        return int(val)
    except Exception:
        return None