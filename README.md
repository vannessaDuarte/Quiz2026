# Taller mecánico (Django)

Aplicación sencilla que cubre la mayoría de los requerimientos de `requerimientos.csv`.
**No tiene usuarios ni contraseñas**: al entrar eliges un rol (Administrador, Recepcionista,
Mecánico o Cliente) y el sistema muestra solo lo que corresponde a ese rol.

## Cómo ejecutarla

### Con Docker (PostgreSQL, usando tu `.env`)
```bash
docker compose up --build
```
Al iniciar, el contenedor genera las migraciones, migra la BD, carga datos de ejemplo
(`cargar_demo`, solo si la BD está vacía) y levanta el servidor en http://localhost:8000

### Sin Docker (SQLite, para probar rápido)
Borra o renombra `.env` (si no existe `POSTGRES_HOST` usa SQLite) y:
```bash
pip install -r requirements.txt
python manage.py makemigrations clientes taller ordenes facturacion
python manage.py migrate
python manage.py cargar_demo
python manage.py runserver
```

## Flujo de una orden
1. **Recepcionista**: registra cliente → vehículos → crea la orden (estado *Recibido*, con fecha).
2. **Administrador**: asigna un mecánico libre (*En diagnóstico*) → el mecánico recibe notificación.
3. **Mecánico**: registra diagnóstico, repuestos (descuentan stock) y mano de obra → "Enviar al cliente"
   (*Esperando aprobación*; se crea notificación y se imprime un correo en consola).
4. **Cliente**: aprueba o rechaza → se notifica a recepción y administrador.
5. **Recepcionista**: genera la orden de reparación → se avisa al administrador y al mecánico.
   El administrador puede **reasignar** si el mecánico ya no está libre.
6. **Mecánico**: *En reparación* → *Listo para retiro* (botón grande inferior) → se genera la boleta/factura.
7. **Administrador**: ve facturas, aplica descuentos y revisa reportes.

## Cobertura de requerimientos
| Código | Estado | Dónde |
|---|---|---|
| RF-01, RF-02 | ✅ | Clientes / Vehículos |
| RF-03 a RF-10 | ✅ | Órdenes (flujo completo) |
| RF-11 a RF-14 | ✅ | Cliente ve y decide; notificaciones; recepción genera orden |
| RF-15, RF-25 | ✅ | Mecánicos (libre/ocupado y sus órdenes) |
| RF-16 | ✅ | Reasignación en el detalle de la orden |
| RF-17, RF-18, RF-19 | ✅ | Estado por el mecánico; registro de repuestos con descuento de stock |
| RF-20 | ✅ | Notificación al administrador con stock ≤ mínimo |
| RF-21, RF-22, RF-23, RF-27 | ✅ | Facturación (IVA 19 %, descuento %, reporte por mes) |
| RF-24, RF-26, RF-28 | ✅ | Vehículos, Repuestos y Reporte de repuestos |
| RF-29 | ✅ | Proveedores (recepción) — se vinculan a repuestos al crear el repuesto |
| RF-30 | ✅ | Administrador elimina órdenes (si no tienen boleta/factura) |
| RNF-01, RNF-05 | ✅ | Barra inferior fija con botón grande para cambiar estado |
| RNF-02 | ✅ | Bootstrap responsive |
| RNF-03 | ➖ | Consultas con `select_related`/índices; no se hizo prueba de carga |
| RF-31, RNF-04 | ⛔ | Omitidos a propósito (piden usuarios/contraseñas/permisos) |

## Notas
- `/admin/` (Django + Jazzmin) sigue disponible para TI; requiere `python manage.py createsuperuser`.
- `openai` está en `requirements.txt` pero no se usa.
- Los IDs de rol viven en la sesión: sin login, **cualquiera puede elegir cualquier rol**. Úsalo solo en una red de confianza.
