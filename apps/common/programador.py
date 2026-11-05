# apps/common/programador.py
"""
Programador interno de tareas diarias — reemplaza a `celery beat` en
ambientes donde sólo se puede tener UNA consola con el backend
(`python manage.py runserver`) y no hay acceso a cron ni al Programador
de tareas de Windows.

Cómo funciona:
  - Al arrancar el servidor (ver CommonConfig.ready), se lanza un hilo en
    segundo plano dentro del mismo proceso.
  - Cada minuto revisa la hora local (America/Bogota). Cuando ya pasó la
    hora programada de una tarea y ésta no se ha ejecutado hoy, la ejecuta.
  - "Ya se ejecutó hoy" se guarda en la base de datos
    (EjecucionTareaProgramada) y se reclama con un UPDATE condicional, así
    que aunque haya dos procesos o el servidor se reinicie, cada tarea
    corre como máximo una vez al día.
  - Si el servidor estaba apagado a la hora programada, la tarea se
    ejecuta apenas arranque (ese mismo día).
  - Si una tarea falla, queda registrado en el log y en la tabla, y se
    vuelve a intentar al día siguiente.

Se controla con TAREAS_DIARIAS_MODO en el .env:
  - 'proceso' (por defecto): este programador.
  - 'celery': no arranca este programador (las corre celery beat).
  - 'desactivado': no corren automáticamente.
"""
import logging
import os
import sys
import threading
import time
from datetime import time as dtime

from django.conf import settings
from django.db import IntegrityError, close_old_connections
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

_hilo = None
_lock = threading.Lock()


# ---------------------------------------------------------------------- #
# Tareas: mismas que CELERY_BEAT_SCHEDULE (config/settings/base.py)
# ---------------------------------------------------------------------- #

def _enviar_recordatorios_tareas():
    from apps.common.services.notificacion_service import NotificacionService
    creadas = NotificacionService.enviar_recordatorios_tareas(
        dias_anticipacion=getattr(settings, 'RECORDATORIOS_DIAS_ANTICIPACION', 3)
    )
    return f"{len(creadas)} notificaciones generadas."


def _verificar_integridad_documentos():
    from apps.common.services.documento_firma_service import DocumentoFirmaService
    r = DocumentoFirmaService.verificar_integridad_todos()
    return f"{r['verificados']} verificados, {r['alterados']} con alerta."


def _parse_hora(valor, defecto):
    try:
        h, m = str(valor).split(':')
        return dtime(int(h), int(m))
    except Exception:
        logger.warning(f"[Programador] Hora inválida '{valor}', se usa {defecto}.")
        return defecto


def _tareas():
    return [
        ('enviar_recordatorios_tareas',
         _parse_hora(getattr(settings, 'HORA_RECORDATORIOS_TAREAS', '07:00'), dtime(7, 0)),
         _enviar_recordatorios_tareas),
        ('verificar_integridad_documentos',
         _parse_hora(getattr(settings, 'HORA_VERIFICACION_INTEGRIDAD', '02:00'), dtime(2, 0)),
         _verificar_integridad_documentos),
    ]


# ---------------------------------------------------------------------- #
# Ejecución
# ---------------------------------------------------------------------- #

def _reclamar(nombre, hoy, ahora):
    """Devuelve True sólo para el proceso que logra marcar la tarea como
    ejecutada hoy (UPDATE atómico en la BD)."""
    from apps.common.models import EjecucionTareaProgramada
    try:
        EjecucionTareaProgramada.objects.get_or_create(nombre=nombre)
    except IntegrityError:
        pass  # otro proceso la creó al mismo tiempo
    actualizadas = (
        EjecucionTareaProgramada.objects
        .filter(nombre=nombre)
        .filter(Q(ultima_fecha__isnull=True) | Q(ultima_fecha__lt=hoy))
        .update(ultima_fecha=hoy, ultima_ejecucion=ahora)
    )
    return actualizadas == 1


def _registrar_resultado(nombre, resultado, error):
    from apps.common.models import EjecucionTareaProgramada
    EjecucionTareaProgramada.objects.filter(nombre=nombre).update(
        ultimo_resultado=str(resultado)[:2000], ultimo_error=error
    )


def revisar_y_ejecutar():
    """Una pasada del programador. Pública para poder probarla a mano."""
    ahora = timezone.localtime()
    hoy = ahora.date()
    for nombre, hora, funcion in _tareas():
        if ahora.time() < hora:
            continue
        if not _reclamar(nombre, hoy, ahora):
            continue
        logger.info(f"[Programador] Ejecutando '{nombre}'...")
        try:
            resultado = funcion()
            _registrar_resultado(nombre, resultado, error=False)
            logger.info(f"[Programador] '{nombre}' terminó: {resultado}")
        except Exception as exc:
            logger.exception(f"[Programador] '{nombre}' falló.")
            _registrar_resultado(nombre, f"{type(exc).__name__}: {exc}", error=True)


def _bucle():
    time.sleep(getattr(settings, 'PROGRAMADOR_ESPERA_INICIAL_SEG', 20))
    intervalo = getattr(settings, 'PROGRAMADOR_INTERVALO_SEG', 60)
    while True:
        try:
            close_old_connections()
            revisar_y_ejecutar()
        except Exception:
            # p.ej. la tabla aún no existe porque falta `migrate`
            logger.exception("[Programador] Error revisando tareas diarias.")
        finally:
            close_old_connections()
        time.sleep(intervalo)


def _es_proceso_servidor():
    """True sólo en el proceso que realmente atiende peticiones.

    `runserver` con autoreload lanza dos procesos: el vigilante de cambios
    y el que sirve (este último tiene RUN_MAIN=true). Sólo arrancamos en el
    que sirve. También se contempla `--noreload` y el ejecutable `daphne`.
    No arranca con migrate, shell, test, celery, etc.
    """
    argv = sys.argv
    if len(argv) > 1 and argv[1] == 'runserver':
        return os.environ.get('RUN_MAIN') == 'true' or '--noreload' in argv
    ejecutable = os.path.basename(argv[0]).lower() if argv else ''
    return 'daphne' in ejecutable


def iniciar():
    global _hilo
    modo = getattr(settings, 'TAREAS_DIARIAS_MODO', 'proceso')
    if modo != 'proceso' or not _es_proceso_servidor():
        return
    with _lock:
        if _hilo is not None:
            return
        _hilo = threading.Thread(target=_bucle, name='programador-tareas-diarias', daemon=True)
        _hilo.start()
    logger.info("[Programador] Programador interno de tareas diarias iniciado.")
