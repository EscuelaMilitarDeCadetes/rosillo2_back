# Gestión de documentos

Los documentos se almacenan en el servidor de archivos.

No se guardan en la base de datos.

La base de datos solo guarda la ruta.

## Rutas de almacenamiento

CONVOCATORIA
PRESUPUESTO
PROYECTO
TRABAJO_GRADO
PLANTILLA

## Tablas utilizadas 
DocumentoFirma 
DocumentoFirmante 
TipoDocumento 
PlantillaDocumento 

## Punto de entrada para escritura en disco 

`DocumentoFirmaService.crear_desde_archivo()` (módulo `common`) es el único punto de entrada permitido para registrar un documento a partir de un archivo subido por multipart: guarda el binario con `default_storage.save()` dentro de `MEDIA_ROOT/<carpeta>` y luego delega en `crear()` para el registro y el cálculo de `hash_documento`. Ningún service de otro módulo debe llamar a `default_storage.save()` directamente para este propósito. 
