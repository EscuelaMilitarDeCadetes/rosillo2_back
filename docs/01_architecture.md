# Arquitectura del sistema

La plataforma está dividida en módulos Django.


## Módulos principales
**`usuarios`**: Gestiona todo lo relacionado con la autenticación, perfiles de usuario, roles, permisos y la asignación histórica de personas a cuentas de usuario.  
**`common`**: Contiene modelos y lógica transversales que son utilizados por múltiples módulos. Incluye el sistema de firma digital, plantillas, historial de actividades y notificaciones.
**`crm`**: Un CRM(Customer Relationship Management) centrado en la investigación institucional.
**`institucional`**: Modela la estructura organizativa de la institución y las relaciones entre ellas.
**`integracion`**: Modela la relación entre el modulo usuarios y el modulo institucional, por lo tanto no contiene ni añade ninguna tabla adicional.
**`investigacion_formal`**: Contiene toda la lógica para el flujo de investigación formal, pasando por el seguimiento y la calificación, hasta la gestión de productos.
**`investigacion_formativa`**: Gestiona los once (11) procesos de opción de grado definidos por la institución (A–K), desde el trabajo de Grado hasta semilleros, pasantías, coautorías, minors, diplomados y cátedras internacionales. Implementa un motor de flujo de trabajo parametrizable y versionable que permite configurar el ciclo de vida de cada modalidad desde la base de datos, sin modificar código.



# Lógica de Negocio y Flujos de Trabajo
Este documento describe los procesos de negocio clave que la plataforma soporta.


## Reglas de negocio institucionales
## Regla RN-06. Ubicación del metodo para crear usuario
Se llegó a la conclusión de que la mejor solución para este proyecto es dejar toda la creación y eliminación (soft-delete) de los registros de las tablas Usuario, RolXUsuario y UsuarioXPersona exclusivamente en el modulo integración y dejar creacion de los registros de las tabla Roles y la asignación y modificación de los registros de las tablas Usuario, Roles, RolXUsuario y UsuarioXPersona al modulo usuarios

## Regla RN-07. Vinculación de investigadores a grupos

Toda persona debe encontrarse vinculada previamente a una Facultad antes de poder registrarse como integrante de un Grupo de Investigación.
Durante la creación o actualización de una relación PersonaXGrupo el sistema verifica automáticamente:
- existencia de una vinculación activa a una Facultad;
- existencia de una relación Facultad → Grupo en FacultadXGrupo; 
- que el grupo seleccionado corresponda exactamente al grupo asignado a la Facultad.
En caso contrario se genera un ValidationError y la operación es cancelada.


## Roles Principales
- **Asesor:** Asesor de investigación del departamento I+D+i que en otras funciones se encarga de crear y cargará las convocatorias internas creadas tanto financiadas como no financiadas.
- **Cexterno (Convocatorias Externas):** Gestiona proyectos de convocatorias externas y gestionan la documentación de los proyectos que participaron en una convocatoria externa.
- **Cinterno (Convocatorias Internas):** Gestiona convocatorias internas, su calificación y gestionan la documentación de los proyectos que participaron en una convocatoria interna y la aprobaron.
- **Decano:** Seguimiento global y aprobación de tareas realizadas.
- **Estudiante:** Puede consultar la disponibilidad de las distintas modalidades en su facultad, escoger una e iniciar una propuesta en ese ambito y cada uno debe firmar la propuesta presentada desde su propio perfil.
- **Facultad:** Actores principales que crean y gestionan proyectos, además de aprobar postulaciones a tesis de grado, asignar los tutores,  realizar seguimiento mensual a las tesis de grado, asignar jurados y establecer lugar y hora para la sustentación y subir concepto posterior a esta.
- **Gerente:** Como responsable legal de todos los proyectos debe firmar y tener con acceso a estadísticas y seguimiento global.
- **Grupo:** Actores principales que crean y gestionan proyectos.
- **Jurado:** Emite un concepto y nota sobre la modalidad de grado iniciada si corresponde.
- **Soporte:** Gestiona usuarios, personas y roles.
- **Supervisor:** Rol de solo lectura con acceso a estadísticas y seguimiento global.
- **Tutor:** Realiza seguimiento mensual del avance en la tesis de grado asignada y acompañamiento al desarrollo de la modalidad de grado iniciada.



## Flujo de Investigación Formal
1.  **Creación y asignación de tareas:** El rol `cinternos` crea las tareas en el flujo y le asigna un responble y la fecha de cumplimiento proyectada.
2.  **Creación de Convocatoria:** El rol `cinternos` crea una convocatoria interna.
3.  **Participación:** Roles `grupos` o `facultades` postulan proyectos a convocatorias activas.
4.  **Cierre y Calificación:** `cinternos` cierra la convocatoria y realiza un proceso de calificación en 6 fases. Se permite la corrección y reenvío por parte de los participantes.
5.  **Aprobación:** Los proyectos que superan las 6 fases cambian su estado a "APROBADO".
    - *Excepción:* Proyectos de `cexternos` se aprueban automáticamente.
6.  **Configuración del Proyecto:** Se asignan fechas, investigadores, producción, objetivos y presupuesto (si aplica).
7.  **Seguimiento Mensual:**
    - `grupos` y `facultades` registran avances.
    - Se genera automáticamente la "Ficha Técnica de Seguimiento" con cálculos de indicadores.
8.  **Gestión y Cierre:** Roles `cinternos` y `cexternos` pueden editar fechas, documentos, producción, etc., y finalmente cerrar el proyecto con un acta.
9. **Seguimiento y estadisticas:** El Rol `supervisor` en cualquier momento puede hacer un seguimiento a proyectos en curso o finalizados y generar estadisticas basados en los datos guardados previamente.
10. **Aprobación:** El Rol `supervisor` aprueba tanto documentos generados como tareas realizadas como el encargado del proyecto.



## Flujo de Investigación Formativa
## A- Trabajo de grado para pregrado
1.  **Registro:** El rol `facultades` registra como usuarios a los estudiantes, tutores y jurados.
2.  **Creación y asignación de tareas:** El rol `facultades` crea las tareas en el flujo y le asigna un responble y la fecha de cumplimiento proyectada.
3.  **Inscripción:** Un `estudiante` elige una idea del `BancoIdeas` y puede agregar compañeros. Se genera el "Formato de inscripción" y la postula para aprobación. El `BancoIdeas` guarda son las areas o ejes tematicos generales sobre los que pueden trabajar ya que el titulo lo definen en una etapa posterior. Las areas o ejes tematicos se pueden repetir pero los titulos deben ser únicos.
4.  **Aprobación fase I y Asignación fase I:** El rol `facultades` aprueba la propuesta y asigna uno o dos `tutores`. Se genera la "Solicitud de aprobación temática".
5.  **Aprobación fase II:** El rol `estudiante` define junto con el `tutor` el título, justificación, objetivos entre otros requisitos y genera el formato de aprobación temática.
5.  **Aprobación fase III:** El rol `facultades` aprueba la propuesta y puede sugerir cambios al documento.
6. **Corrección fase I:** El `estudiante` realiza la corrección al documento según sugerencias.
7.  **Asignación fase II:** El rol `facultades` asigna a los dos `jurado` que evaluaran la tesis de grado.
8.  **Ejecución:** El `estudiante` realiza el anteproyecto con ayuda del `tutor`.
9.  **Seguimiento fase I:** El `tutor` sube avances mensualmente.
10.  **Evaluación fase I:** El rol `tutor` sube un documento y emite una nota sobre ese documento si el tutor entrega tarde el documento ingresa a la SEGUNDA INSTANCIA.
11. **Concepto fase I:** El rol `facultades` revisa el porcentaje de similitud del anteproyecto entregado en un software anti-plagio si no supera cierto porcentaje el proceso continua de lo contrario se devuelve el documento para corrección.
12. **Corrección fase II:** El `estudiante` realiza la corrección al documento según sugerencias y entrega documento corregido.
13.  **Concepto fase II:** El rol `facultades` revisa el porcentaje de similitud del anteproyecto entregado en un software anti-plagio si no supera cierto porcentaje el proceso continua de lo contrario ingresa a la SEGUNDA INSTANCIA.
14.  **Revisión fase I:** El rol `facultades` envia documento a los `jurados` para revisión.
15. **Concepto fase III:** El rol `jurado` revisa el documento y cada uno emite un concepto si el puntaje es inferior a 3.5 ingresa a la SEGUNDA INSTANCIA de lo contrario sigue el proceso normal.
En el caso de que uno de los jurados apruebe el documento y el otro lo rechace.
16. **Discrepancia fase I:** El rol `facultades` asigna a los un tercer `jurado` para que emita su concepto definitivo
17. **Discrepancia fase II:** El rol `jurado` emite su concepto definitivo sobre el documento en disputa.
18. **Centralización:** El rol `facultades` centraliza la información de los jurados y envía los documentos a través de un correo electrónico al `estudiante`.
19. **Corrección fase III:** El `estudiante` realiza la corrección al documento según sugerencias y entrega documento corregido.
20. **Revisión fase II:** El rol `facultades` envia documento corregido a los `jurado` para revisión.
21. **Concepto fase IV:** El rol `jurado` revisa el documento corregido y cada uno emite una nota sobre ese documento si el puntaje es inferior a 3.5 ingresa a la SEGUNDA INSTANCIA de lo contrario sigue el proceso normal.
22. **Sustentación fase I:** El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
23. **Sustentación fase II:** Los `estudiante` realizan la sustentación.
19. **Sustentación fase III:** Cada rol `jurado` emite concepto y nota si el puntaje es inferior a 3.5 ingresa a la SEGUNDA INSTANCIA de lo contrario sigue el proceso normal.
20. **Consolidado:**: El rol `facultades` consolida las notas del tutor, la primera de los jurados y la segunda de los jurados ponderando lo anterior en una nota final si la nota final es inferior a 3.5 ingresa a la SEGUNDA INSTANCIA y deben volver a sustentar una semana después de lo contrario sigue el proceso normal de generación de documentación y certificados.
21. **Seguimiento fase II:** El `tutor` entrega consolidado con los seguimientos mensuales.
22. **Aprobación:** El Rol `supervisor` aprueba tanto documentos generados como tareas realizadas como el encargado del proyecto.
La SEGUNDA INSTANCIA es la última oportunidad que tienen los `estudiante` para aprobar su anteproyecto, solo se puede 'activar' si sucede una unica vez alguno de los casos mencionados arriba y representa su segunda y ultima oportunidad cuya nota maxima no puede ser superior a 3.5, si llega a suspender se debe iniciar el proceso nuevamente con una idea o proyecto diferente.

## B- Participación en el Programa de Semilleros de Investigación de la ESMIC
1. El rol `facultades` abre las convocatorias según la disponibilidad reportada por los semilleros.
2. El rol `estudiante` se postula en alguna de las convocatorias abiertas.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` crea y asigna el proyecto formalmente.
5. El rol `facultades` asigna un investigador principal normalmente el `tutor`.
6. El rol `facultades` inscribe el proyecto como opción de grado.
7. El rol `facultades` entrega al `estudiante` el plan de trabajo propuesto por el semillero.
8. El rol `tutor` sube avances semestralmente.
9. El rol `tutor` registra las actividades realizadas 
10. El rol `estudiante` con ayuda del `tutor` genera producto CTeI
11. El rol `estudiante` participa en evento cientifico
12. El rol `estudiante` entrega certificado del evento cientifico en el que participó
13. El rol `tutor` realiza una especie de evalución en su rol como investigador principal
14. El rol `facultades` evalua los productos
15. El rol `tutor` emite calficación final
16. El rol `facultades` realiza el acta y le da cierre al proyecto.

## C- Coautoría y redacción de artículos científicos e informes técnicos
1. El rol `facultades` crea las postulaciones para la redacción de artículos científicos e informes técnicos.
2. El rol `estudiante` se postula en alguna de las vacantes abiertas.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` crea y asigna el proyecto formalmente.
5. El rol `facultades` asigna un investigador principal o `tutor`.
6. El rol `estudiante` con ayuda del `tutor` definen el plan de trabajo.
7. El rol `facultades` asigna el producto científico.
8. El rol `estudiante` realiza la invesigación documental.
9. El rol `estudiante` hace la redacción de los borradores.
10. El rol `tutor` realiza la revisión científica de lo que el `estudiante` redactó.
11. El rol `tutor` sugiere correcciones al documento.
12. El rol `estudiante` realiza las correcciones al documento.
13. El rol `estudiante` entrega el producto final.
14. El rol `tutor` realiza la validación, aceptación y publicación de documento.
15. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
16. El rol `estudiante` realiza la sustentación.
17. El rol `tutor` emite concepto y nota, es decir, califica la sustentación.
18. El rol `facultades` realiza el acta y le da cierre al proyecto.

## D- Coautoría de un proyecto de desarrollo tecnológico e innovación
1. El rol `facultades` crea las postulaciones para la coautoría de un proyecto de desarrollo tecnológico e innovación.
2. El rol `estudiante` se postula en alguna de las vacantes abiertas.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` crea y asigna el proyecto formalmente.
5. El rol `facultades` asigna un investigador principal normalmente el `tutor`.
6. El rol `estudiante` con ayuda del `tutor` definen el plan de trabajo.
7. El rol `estudiante` realiza la desarrollo del prototipo o modelo.
8. El rol `tutor` realiza el seguimiento técnico del prototipo o modelo.
9. El rol `estudiante` con ayuda del `tutor` realizan las pruebas y validación del prototipo o modelo.
10. El rol `estudiante` entrega el producto tecnológico.
11. El rol `tutor` realiza la evaluación técnica del prototipo o modelo.
12. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
13. El rol `estudiante` realiza la sustentación.
14. El rol `tutor` emite concepto y nota, es decir, califica la sustentación.
15. El rol `facultades` realiza el acta y le da cierre al proyecto.

## E- Asistente de investigación
1. El rol `facultades` crea las postulaciones para el asistente de investigación.
2. El rol `estudiante` se postula en alguna de las vacantes abiertas.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` crea y asigna el proyecto formalmente.
5. El rol `facultades` asigna un investigador principal normalmente el `tutor`.
6. El rol `estudiante` con ayuda del `tutor` definen el plan de trabajo.
7. El rol `estudiante` realiza las actividades investigativas.
8. El rol `tutor` realiza el seguimiento a las horas de trabajo.
9. El rol `tutor` reporta las actividades realizadas por el `estudiante`.
10. El rol `facultades` crea y envia el certificado de cumplimiento al `tutor` y `estudiante`.
11. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
12. El rol `estudiante` realiza la sustentación y entrega el informe final.
13. El rol `tutor` emite concepto y nota, es decir, califica la sustentación.
14. El rol `facultades` realiza el acta y le da cierre al proyecto.

## F- Pasantía dentro de los centros y/o grupos de investigación de la ESMIC
1. El rol `facultades` abre las convocatorias según la disponibilidad reportada por los centros y/o grupos de investigación.
2. El rol `estudiante` se postula en alguna de las convocatorias abiertas.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` crea y asigna el proyecto formalmente.
5. El rol `facultades` asigna al `estudiante` al centro y/o grupo de investigación.
6. El rol `facultades` asigna un investigador principal normalmente el `tutor`.
7. El rol `facultades` entrega al `estudiante` el plan de trabajo propuesto por el centro y/o grupo de investigación.
8. El rol `estudiante` ejecuta las actividades.
9. El rol `tutor` realiza el seguimiento a las horas de trabajo. 
10. El rol `estudiante` con ayuda del `tutor` genera el informe técnico.
11. El rol `facultades` crea y envia el certificado de cumplimiento al `tutor`.
12. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
13. El rol `estudiante` realiza la sustentación.
14. El rol `tutor` emite concepto y nota, es decir, califica la sustentación.
15. El rol `facultades` realiza el acta y le da cierre al proyecto.

## G- Pasantía dentro del Observatorio de Equidad de Género, Seguridad y Fuerza Pública
1. El rol `facultades` abre las convocatorias para la pasantía dentro del Observatorio de Equidad de Género, Seguridad y Fuerza Pública.
2. El rol `estudiante` se postula en alguna de las convocatorias abiertas.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` crea y asigna el proyecto formalmente.
5. El rol `facultades` asigna al `estudiante` al centro y/o grupo de investigación.
6. El rol `facultades` asigna un investigador principal normalmente el `tutor`.
7. El rol `facultades` entrega al `estudiante` el plan de trabajo propuesto por el centro y/o grupo de investigación.
8. El rol `estudiante` ejecuta las actividades.
9. El rol `tutor` realiza el seguimiento a las horas de trabajo. 
10. El rol `estudiante` con ayuda del `tutor` genera el informe técnico.
11. El rol `facultades` crea y envia el certificado de cumplimiento al `tutor`.
12. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
13. El rol `estudiante` realiza la sustentación.
14. El rol `tutor` emite concepto y nota, es decir, califica la sustentación.
15. El rol `facultades` realiza el acta y le da cierre al proyecto.

## H- Minors
1. El rol `facultades` abre las ofertas a los minors.
2. El rol `estudiante` se inscribe en el minor en cuestion.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` matricula al `estudiante` al minor como asignatura.
5. El rol `estudiante` asiste al minor.
6. El rol `facultades` genera el certificado de constancia de asistencia.
7. El rol `facultades` registra las calificaciones del `estudiante`.
8. El rol `facultades` valida las 120 horas del `estudiante`.
9. El rol `facultades` carga el certificado de aprobación. 
10. El rol `estudiante` entrega el ensayo o caso de estudio.
11. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
12. El rol `estudiante` realiza la sustentación.
13. El rol `facultades` emite concepto y nota, es decir, califica la sustentación.
14. El rol `facultades` realiza el acta y le da cierre al proyecto.

## I- Diplomado de profundización
1. El rol `facultades` abre las ofertas de diplomados.
2. El rol `estudiante` se inscribe en el diplomado en cuestion.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
6. El rol `estudiante` asiste al diplomado.
7. El rol `facultades` contabiliza las horas de asistencia del `estudiante` al diplomado.
8. El rol `facultades` carga el certificado de aprobación.
9. El rol `estudiante` entrega el ensayo o caso de estudio.
10. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
11. El rol `estudiante` realiza la sustentación.
12. El rol `facultades` emite concepto y nota, es decir, califica la sustentación.
13. El rol `facultades` realiza el acta y le da cierre al proyecto.

## J- Cátedra internacional en investigación o profundización
1. El rol `facultades` registra el curso internacional según soicitud.
2. El rol `facultades` valida el ORI de la institución.
3. El rol `facultades` aprueba el lugar donde se realizará el curso
4. El rol `estudiante` se inscribe en el curso internacional en cuestion.
5. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
6. El rol `estudiante` asiste al curso internacional.
7. El rol `facultades` carga el certificado de aprobación.
8. El rol `facultades` valida las 120 horas del `estudiante`.
9. El rol `estudiante` entrega el ensayo o caso de estudio.
10. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
11. El rol `estudiante` realiza la sustentación.
12. El rol `facultades` emite concepto y nota, es decir, califica la sustentación.
13. El rol `facultades` realiza el acta y le da cierre al proyecto.

## K- Elaboración y documentación de estudio de caso
1. El rol `facultades` define el estudio de caso.
2. El rol `estudiante` se postula en el estudio de caso.
3. El rol `facultades` valida si el `estudiante` cumple con todos los requisitos académicos requeridos.
4. El rol `facultades` aprueba el estudio de caso.
5. El rol `facultades` asigna un investigador principal normalmente el `tutor`.
6. El rol `facultades` entrega al `estudiante` el plan de trabajo.
7. El rol `estudiante` realiza la investigación o análisis del estudio de caso.
8. El rol `estudiante` entrega el documento técnico del estudio de caso.
9. El rol `tutor` realiza la revisión del documento técnico del estudio de caso.
10. El rol `tutor` sugiere correcciones al documento.
11. El rol `estudiante` realiza las correcciones al documento.
12. El rol `estudiante` entrega el documento corregido.
13. El rol `facultades` asigna a los dos `jurado` que evaluaran el documento técnico del estudio de caso
14. El rol `facultades` envia documento a los `jurados` para revisión.
15. El rol `jurado` revisa el documento y hace correcciones al documento.
16. El rol `estudiante` realiza las correcciones al documento.
17. El rol `estudiante` entrega el documento definitivo.
18. El rol `jurado` revisa el documento corregido y emite un concepto y nota.
19. El rol `facultades` asigna fecha, lugar y envía invitaciones para la sustentación.
20. El rol `estudiante` realiza la sustentación.
21. El rol `jurado` emite concepto y nota de la sustentación.
22. El rol `facultades` realiza el acta y le da cierre al proyecto.



## Flujo común en ambas investigaciones
1. **Historial:** Registra todas las acciones realizadas por todos los usuarios en el sistema.
2. **Tarea:** Una "aprobación pendiente" es una Tarea asignada a un usuario específico sobre un objeto específico que se realizan en los procesos **Creación y asignación de tareas** mencionados en los dos flujos anteriores.
3. **Aprobación:** El rol `supervisor` o `decano` aprueban las tareas registradas y asignadas por el rol `cinternos` o `facultades`.
4. **Firmantes:** El rol `cinternos` o `facultades` asignan los firmantes y el orden en el que deben firmar los documentos si alguno de los firmantes rechaza firmar se debe escribir el motivo del rechazo.
5. **Firmas:** Se guardan las rutas de los documentos completamente firmados.
6. **Plantillas:** Se pueden descargar los formatos para diligenciar los documentos.
7. **Notificación:** Sistema de alertas dentro de la app, complementario al email


## Flujo de Rotación de Personal
Para manejar la rotación de personal en roles institucionales (ej. Director de Facultad), se utiliza el modelo `UsuarioXPersona`. Este modelo permite que una cuenta de usuario genérica (ej. `director.facultad.ciencias@...`) sea asignada a diferentes `Personas` a lo largo del tiempo, manteniendo un historial auditable de quién ocupó el cargo y cuándo.
