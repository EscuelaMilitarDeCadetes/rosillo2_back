"""
Crea los tipos de documento que el código de investigación formativa busca
por nombre (TIPO_DOCUMENTO_APROBACION_* en apps/investigacion_formativa).
Si alguno no existe, aprobar una postulación, un participante, una
evaluación, un evento evaluativo o una segunda instancia da error 500.

Es idempotente: si el tipo ya existe (sin importar mayúsculas) no lo toca,
salvo que tenga `investigacion` vacío, en cuyo caso lo marca como formativa.
"""
from django.db import migrations

REQUERIDOS = [
    'APROBACION_POSTULACION',
    'APROBACION_PARTICIPANTE',
    'APROBACION_EVALUACION_PROCESO',
    'APROBACION_EVENTO_EVALUATIVO',
    'APROBACION_SEGUNDA_INSTANCIA',
]


def crear_requeridos(apps, schema_editor):
    TipoDocumento = apps.get_model('common', 'TipoDocumento')
    for nombre in REQUERIDOS:
        existente = TipoDocumento.objects.filter(nombre_documento__iexact=nombre).first()
        if existente is None:
            TipoDocumento.objects.create(
                nombre_documento=nombre,
                grupo='aprobacion',
                investigacion='formativa',
                es_obligatorio=False,
            )
        elif not existente.investigacion:
            existente.investigacion = 'formativa'
            existente.save(update_fields=['investigacion'])


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_ejecuciontareaprogramada'),
    ]

    operations = [
        migrations.RunPython(crear_requeridos, migrations.RunPython.noop),
    ]
