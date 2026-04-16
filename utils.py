import re
import math


def seconds_to_mmss(seconds: float) -> str:
    total = int(math.floor(seconds))
    m, s = divmod(total, 60)
    return f"{m:02d}:{s:02d}"


def sanitize_filename(title: str, max_length: int = 80) -> str:
    name = re.sub(r"[^\w\s\-.]", "_", title)
    name = re.sub(r"[\s_]+", "_", name)
    name = name.strip("_.")
    name = name[:max_length]
    return name or "untitled"
