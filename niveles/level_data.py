import re


def level_options(data):
    if not isinstance(data, dict):
        return []

    palette_options = data.get("palette_options")
    options = data.get("options")
    using_palettes = isinstance(palette_options, list) and bool(palette_options)
    source = palette_options if using_palettes else options
    if not isinstance(source, list):
        return []

    normalized = []
    for option in source:
        if not isinstance(option, dict):
            continue
        option_id = option.get("id")
        if not isinstance(option_id, str) or not option_id:
            continue

        colors = option.get("colors", [])
        if not isinstance(colors, list):
            colors = []
        if isinstance(option.get("color"), str):
            colors = [option["color"], *colors]
        colors = [
            color for color in colors
            if isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color)
        ]
        label = option.get("label")
        if not isinstance(label, str) or not label:
            label = option.get("name")
        if not isinstance(label, str) or not label:
            label = f"{'Paleta' if using_palettes or colors else 'Opción'} {option_id.upper()}"

        normalized.append({
            "id": option_id,
            "label": label,
            "colors": colors,
        })
    return normalized


def correct_option_id(solution):
    if not isinstance(solution, dict):
        return None

    option_id = solution.get("option_id")
    if option_id is None:
        option_id = solution.get("correct_option_id")
    return option_id if isinstance(option_id, str) and option_id else None
