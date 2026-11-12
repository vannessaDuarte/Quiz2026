from django.contrib import messages
from django.shortcuts import redirect, render

from clientes.models import Cliente
from taller.models import Mecanico

from .roles import CLIENTE, MECANICO, ROLES


def inicio(request):
    return render(
        request,
        "core/inicio.html",
        {
            "mecanicos": Mecanico.objects.filter(activo=True),
            "clientes": Cliente.objects.all(),
        },
    )


def elegir_rol(request):
    if request.method != "POST":
        return redirect("inicio")
    rol = request.POST.get("rol")
    actor = request.POST.get("actor_id") or None
    if rol not in dict(ROLES):
        messages.error(request, "Rol no válido.")
        return redirect("inicio")
    if rol == MECANICO and not Mecanico.objects.filter(pk=actor, activo=True).exists():
        messages.error(request, "Elige un mecánico.")
        return redirect("inicio")
    if rol == CLIENTE and not Cliente.objects.filter(pk=actor).exists():
        messages.error(request, "Elige un cliente.")
        return redirect("inicio")
    request.session["rol"] = rol
    request.session["actor_id"] = int(actor) if actor else None
    return redirect("ordenes:lista")


def salir(request):
    request.session.pop("rol", None)
    request.session.pop("actor_id", None)
    return redirect("inicio")
