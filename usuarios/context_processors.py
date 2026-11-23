from .permissions import get_management_sections


def app_navigation(request):
    user = request.user
    current_url_name = getattr(request.resolver_match, "url_name", "")
    management_sections = get_management_sections(user)
    sections = []

    for section in management_sections:
        destination = section["list_url"] if section["can_view"] else section["create_url"]
        sections.append({
            **section,
            "url_name": destination,
            "is_current": current_url_name in section["active_url_names"],
        })
    is_teacher = (
        user.is_authenticated
        and user.is_active
        and not (user.is_staff or user.is_superuser)
        and any(
            section["label"] in {"Niveles del juego", "Progresos"}
            for section in management_sections
        )
    )
    return {
        "app_navigation_sections": sections,
        "app_has_management_access": (
            user.is_authenticated
            and user.is_active
            and (user.is_staff or user.is_superuser or bool(management_sections))
        ),
        "app_is_teacher": is_teacher,
        "app_navigation_is_game_current": current_url_name in {
            "bienvenida_jugador",
            "jugar_nivel",
        },
        "app_navigation_is_dashboard_current": current_url_name == "dashboard_admin",
    }
