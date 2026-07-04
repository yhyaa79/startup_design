# roadmap/templatetags/dashboard_extras.py
import math
from django import template

register = template.Library()


@register.filter(name="radial_arc")
def radial_arc(value, radius=54):
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0
    try:
        radius = float(radius)
    except (TypeError, ValueError):
        radius = 54.0

    circumference = 2 * math.pi * radius
    value = max(0, min(100, value))
    filled = circumference * (value / 100)
    return f"{filled:.2f} {circumference:.2f}"


@register.simple_tag(name="donut_segments")
def donut_segments(stats, radius=54):
    if not stats:
        return []

    total = stats.get("total") or 0
    if not total:
        return []

    try:
        circumference = 2 * math.pi * float(radius)
    except (TypeError, ValueError):
        circumference = 2 * math.pi * 54.0

    keys_colors = [
        ("completed", "#2f5cf5"),
        ("in_progress", "#5f7ef7"),
        ("pending", "#8fa3fa"),
        ("paused", "#bfccfc"),
        ("cancelled", "#e3e9ff"),
    ]

    segments = []
    offset = 0.0
    for key, color in keys_colors:
        val = stats.get(key) or 0
        if not val:
            continue
        frac = val / total
        length = circumference * frac
        segments.append(
            {
                "key": key,
                "color": color,
                "value": val,
                "dasharray": f"{length:.2f} {circumference - length:.2f}",
                "dashoffset": f"{-offset:.2f}",
            }
        )
        offset += length
    return segments


@register.simple_tag(name="line_chart_data")
def line_chart_data(items, value_attr="progress", width=640, height=180, padding=36):
    def get_val(item):
        if isinstance(item, dict):
            return item.get(value_attr, 0) or 0
        return getattr(item, value_attr, 0) or 0

    items = list(items or [])
    n = len(items)
    if n == 0:
        return {"points": "", "area_points": "", "nodes": []}

    width, height, padding = float(width), float(height), float(padding)

    if n == 1:
        xs = [width / 2]
    else:
        xs = [padding + i * (width - 2 * padding) / (n - 1) for i in range(n)]

    nodes = []
    for x, item in zip(xs, items):
        val = get_val(item)
        y = height - padding - (val / 100) * (height - 2 * padding)
        nodes.append({"x": round(x, 1), "y": round(y, 1), "item": item, "value": val})

    points = " ".join(f"{node['x']},{node['y']}" for node in nodes)
    baseline = height - padding
    area_points = f"{nodes[0]['x']},{baseline} " + points + f" {nodes[-1]['x']},{baseline}"

    return {"points": points, "area_points": area_points, "nodes": nodes}


@register.filter(name="dget")
def dget(d, key):
    try:
        return d.get(key)
    except AttributeError:
        return None


@register.filter(name="get_item")
def get_item(d, key):
    try:
        return d.get(key)
    except (AttributeError, TypeError):
        return None


@register.simple_tag(name="list_max")
def list_max(items, field, default=1):
    try:
        vals = [item.get(field) or 0 for item in items]
        return max(vals) if vals else default
    except (AttributeError, TypeError):
        return default


@register.simple_tag(name="bar_height")
def bar_height(value, max_value, max_px=54, min_px=6):
    try:
        value = float(value or 0)
        max_value = float(max_value) or 1
        h = (value / max_value) * float(max_px)
        return round(max(h, min_px), 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return min_px


@register.simple_tag(name="bar_width")
def bar_width(value, max_value, max_pct=100, min_pct=4):
    try:
        value = float(value or 0)
        max_value = float(max_value) or 1
        w = (value / max_value) * float(max_pct)
        return round(max(w, min_pct), 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return min_pct


@register.simple_tag(name="donut_gradient")
def donut_gradient(stats):
    order = [
        ("completed", "#2f5cf5"),
        ("in_progress", "#5f7ef7"),
        ("pending", "#8fa3fa"),
        ("paused", "#bfccfc"),
        ("cancelled", "#e3e9ff"),
    ]
    try:
        total = float(stats.get("total") or 0)
    except (AttributeError, TypeError):
        total = 0

    if not total:
        return "conic-gradient(#e3e9ff 0% 100%)"

    segments = []
    acc = 0.0
    for key, color in order:
        val = float(stats.get(key) or 0)
        if val <= 0:
            continue
        pct = (val / total) * 100
        segments.append(f"{color} {acc:.2f}% {acc + pct:.2f}%")
        acc += pct

    if acc < 100:
        segments.append(f"#eef0f4 {acc:.2f}% 100%")

    return "conic-gradient(" + ", ".join(segments) + ")"


@register.filter(name="status_color")
def status_color(status):
    return {
        "ahead": "#1ea672",
        "on_track": "#2f5cf5",
        "behind": "#e0553f",
    }.get(status, "#6b7080")


@register.filter(name="persian_status")
def persian_status(status):
    return {
        "ahead": "جلوتر از برنامه",
        "on_track": "مطابق برنامه",
        "behind": "عقب‌تر از برنامه",
    }.get(status, "نامشخص")


@register.filter(name="level_label")
def level_label(level):
    return {
        "critical": "بحرانی",
        "high": "زیاد",
        "medium": "متوسط",
        "low": "کم",
    }.get(level, level)
