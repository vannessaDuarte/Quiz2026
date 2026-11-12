"""Control de acceso simple por rol (sin usuarios ni contraseñas).

El rol activo se guarda en la sesión. Para mecánico y cliente también se guarda
quién es (actor_id), de modo que cada uno vea solo lo suyo.
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

ADMIN = "admin"
RECEPCION = "recepcion"
MECANICO = "mecanico"
CLIENTE = "cliente"

ROLES = [
    (ADMIN, "Administrador"),
    (RECEPCION, "Recepcionista"),
    (MECANICO, "Mecánico"),
    (CLIENTE, "Cliente"),
]


def rol_actual(request):
    return request.session.get("rol")


def actor_id(request):
    return request.session.get("actor_id")


def get_actor(request):
    from clientes.models import Cliente
    from taller.models import Mecanico

    rol, aid = rol_actual(request), actor_id(request)
    if rol == MECANICO and aid:
        return Mecanico.objects.filter(pk=aid).first()
    if rol == CLIENTE and aid:
        return Cliente.objects.filter(pk=aid).first()
    return None


def notificaciones_de(request):
    from taller.models import Notificacion

    rol, aid = rol_actual(request), actor_id(request)
    qs = Notificacion.objects.filter(destino=rol)
    if rol == MECANICO:
        qs = qs.filter(mecanico_id=aid)
    elif rol == CLIENTE:
        qs = qs.filter(cliente_id=aid)
    return qs.select_related("orden")


def rol_requerido(*roles):
    def decorador(vista):
        @wraps(vista)
        def envoltorio(request, *args, **kwargs):
            rol = rol_actual(request)
            if not rol:
                messages.info(request, "Primero elige cómo quieres ingresar.")
                return redirect("inicio")
            if rol not in roles:
                messages.error(request, "No tienes permiso para entrar a esa sección.")
                return redirect("ordenes:lista")
            return vista(request, *args, **kwargs)

        return envoltorio

    return decorador
