from .models import Notificacion


def notificar(destino, mensaje, orden=None, mecanico=None, cliente=None):
    return Notificacion.objects.create(
        destino=destino, mensaje=mensaje, orden=orden, mecanico=mecanico, cliente=cliente
    )
