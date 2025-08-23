from python.config import APPS_JSON_URL, fetch_json, APPS_JSON_LOCAL


def load_apps():
    sections = fetch_json(APPS_JSON_URL, APPS_JSON_LOCAL)

    if isinstance(sections, dict):
        print("[DEBUG] apps.json dict keys:", list(sections.keys()))
        if "apps" in sections:
            sections = sections["apps"]
        else:
            raise ValueError(f"Invalid apps.json format: dict keys = {list(sections.keys())}")

    if not isinstance(sections, list):
        raise ValueError(f"apps.json must be a list, got: {type(sections)}")

    print(f"[DEBUG] Loaded {len(sections)} sections")
    print("[DEBUG] First item:", sections[0])

    catalog = []
    for section in sections:
        if "section" not in section or "apps" not in section:
            raise ValueError(f"Invalid section object: {section}")

        catalog.append(
            {
                "section": section["section"],
                "name": f"-- All in {section['section']} --",
                "id": f"section-all-{section['section']}",
                "is_section_toggle": True,
            }
        )
        for app in section["apps"]:
            catalog.append(
                {
                    "section": section["section"],
                    "name": app["name"],
                    "id": app["id"],
                    "is_section_toggle": False,
                }
            )
    return catalog