from .roles import ROLES, get_actor, notificaciones_de, rol_actual


def contexto(request):
    rol = rol_actual(request) if hasattr(request, "session") else None
    ctx = {"rol": rol, "rol_label": dict(ROLES).get(rol), "actor": None, "n_notif": 0}
    if rol:
        ctx["actor"] = get_actor(request)
        ctx["n_notif"] = notificaciones_de(request).filter(leida=False).count()
    return ctx
