import json
import math
import re
from collections import Counter
from typing import Any

WORDS = re.compile(r"[A-Za-z0-9']+")


def analyze_text(text: str) -> dict[str, Any]:
    words = WORDS.findall(text)
    normalized = [word.casefold() for word in words]
    counts = Counter(normalized)
    return {
        "character_count": len(text), "character_count_excluding_spaces": sum(not c.isspace() for c in text),
        "word_count": len(words), "unique_word_count": len(counts),
        "sentence_count": len(re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", text.strip())) if text.strip() else 0,
        "average_word_length": round(sum(map(len, words)) / len(words), 2) if words else 0,
        "most_frequent_words": [{"word": word, "count": count} for word, count in counts.most_common(10)],
        "estimated_reading_time_minutes": round(len(words) / 200, 2),
        "uppercase_count": sum(c.isupper() for c in text), "lowercase_count": sum(c.islower() for c in text),
        "digit_count": sum(c.isdigit() for c in text),
        "special_character_count": sum(not c.isalnum() and not c.isspace() for c in text),
    }


def inspect_json(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
    encoded = json.dumps(payload)
    if len(encoded.encode()) > 200_000:
        raise ValueError("JSON payload exceeds the 200 KB inspection limit")
    stats = {"total_keys": 0, "maximum_depth": 0, "objects": 0, "arrays": 0, "strings": 0, "numbers": 0, "booleans": 0, "nulls": 0}
    paths: list[str] = []
    def walk(value: Any, path: str, depth: int) -> None:
        if depth > 30:
            raise ValueError("JSON nesting exceeds the maximum depth of 30")
        stats["maximum_depth"] = max(stats["maximum_depth"], depth)
        if isinstance(value, dict):
            stats["objects"] += 1; stats["total_keys"] += len(value)
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else str(key)
                if len(paths) < 200: paths.append(child_path)
                walk(child, child_path, depth + 1)
        elif isinstance(value, list):
            stats["arrays"] += 1
            for index, child in enumerate(value):
                child_path = f"{path}[{index}]"
                if len(paths) < 200: paths.append(child_path)
                walk(child, child_path, depth + 1)
        elif value is None: stats["nulls"] += 1
        elif isinstance(value, bool): stats["booleans"] += 1
        elif isinstance(value, (int, float)): stats["numbers"] += 1
        elif isinstance(value, str): stats["strings"] += 1
    walk(payload, "$", 1)
    return {"json_type": "object" if isinstance(payload, dict) else "array", **stats, "pretty_json": json.dumps(payload, indent=2, ensure_ascii=False), "flattened_key_paths": paths, "paths_truncated": len(paths) == 200}


def transform_data(request: Any) -> dict[str, Any]:
    items = list(request.items)
    if request.search:
        needle = request.search.casefold(); items = [i for i in items if needle in f"{i['name']} {i['category']}".casefold()]
    if request.category:
        items = [i for i in items if i["category"].casefold() == request.category.casefold()]
    items.sort(key=lambda item: item[request.sort_by].casefold() if isinstance(item[request.sort_by], str) else item[request.sort_by], reverse=request.sort_order == "desc")
    total = len(items); start = (request.page - 1) * request.page_size
    return {"items": items[start:start + request.page_size], "pagination": {"page": request.page, "page_size": request.page_size, "total_items": total, "total_pages": math.ceil(total / request.page_size), "has_next": start + request.page_size < total, "has_previous": request.page > 1}}
