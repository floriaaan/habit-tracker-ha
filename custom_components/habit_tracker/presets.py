"""Suggested habits, never created until the user confirms the form."""

# name EN/FR, category, kind, unit, target, period, step, icon, color
PRESETS = {
    "reading": ("Reading", "Lecture", "mind", "boolean", "count", 1, "daily", 1, "mdi:book-open-variant", "#a996c8"),
    "meditation": ("Meditation", "Méditation", "mind", "duration", "seconds", 600, "daily", 60, "mdi:meditation", "#a996c8"),
    "tidying": ("Tidying", "Rangement", "daily", "boolean", "count", 1, "daily", 1, "mdi:broom", "#cfaa70"),
    "water": ("Hydration", "Hydratation", "nutrition", "quantity", "milliliters", 2000, "daily", 250, "mdi:water", "#75b7ad"),
    "produce": ("Fruit and vegetables", "Fruits et légumes", "nutrition", "quantity", "count", 5, "daily", 1, "mdi:food-apple-outline", "#91ae85"),
    "running": ("Running", "Course", "sport", "quantity", "meters", 25000, "weekly", 1000, "mdi:run", "#6e9cc7"),
    "swimming": ("Swimming", "Natation", "sport", "quantity", "meters", 3000, "weekly", 100, "mdi:swim", "#75b7ad"),
}


def defaults(preset, language, timezone):
    values = PRESETS.get(preset, ("", "", "daily", "boolean", "count", 1, "daily", 1, "mdi:check-circle-outline", "#cfaa70"))
    en, fr, category, kind, unit, target, period, step, icon, color = values
    return {"name": fr if language.startswith("fr") else en, "category": category,
            "kind": kind, "unit": unit, "target": target, "period": period,
            "step": step, "timezone": timezone, "icon": icon, "color": color}
