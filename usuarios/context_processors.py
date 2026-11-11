from .permissions import get_management_sections, has_management_access


def app_navigation(request):
    user = request.user
    current_url_name = getattr(request.resolver_match, "url_name", "")
    sections = []

    for section in get_management_sections(user):
        destination = section["list_url"] if section["can_view"] else section["create_url"]
        sections.append({
            **section,
            "url_name": destination,
            "is_current": current_url_name in section["active_url_names"],
        })

    return {
        "app_navigation_sections": sections,
        "app_has_management_access": has_management_access(user),
        "app_navigation_is_game_current": current_url_name in {
            "bienvenida_jugador",
            "jugar_nivel",
        },
        "app_navigation_is_dashboard_current": current_url_name == "dashboard_admin",
    }
