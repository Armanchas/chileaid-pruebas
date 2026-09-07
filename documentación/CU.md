# Casos de Uso — Chile Aid

Especificación de los casos de uso de la plataforma Chile Aid (gestión de donaciones humanitarias). Actores del sistema: **Visitante**, **Donante Particular**, **Organización Receptora** y **Administrador del Sistema**.

---

## Identificador: CU-01

**Nombre**
Registrar organización receptora

**Actores**
Visitante (Organización Receptora)

**Descripción**
La Organización ingresa sus datos y documentos para solicitar acceso a la plataforma, quedando en estado pendiente de aprobación por el Administrador del Sistema.

**Pre condiciones**
1. El usuario no debe tener una sesión iniciada.
2. El email de la organización no debe estar registrado previamente en la plataforma.

**Flujo principal**
1. El usuario accede al formulario de registro de organización.
2. El usuario ingresa los datos de la organización: nombre, tipo de centro (centro de acopio, punto de distribución o ambos), RUT (opcional), región, dirección, nombre del contacto, email, teléfono, contraseña y confirmación de contraseña.
3. El usuario selecciona la opción registrar.
4. El sistema valida los datos ingresados (campos obligatorios, formato del email, región dentro del catálogo nacional, coincidencia de las contraseñas).
5. El sistema crea la cuenta representante y la organización en estado "pendiente".
6. El sistema informa al usuario que la solicitud quedó pendiente de aprobación.

**Flujo alternativo**
4.1 El email ya está registrado en la plataforma.
4.2 El sistema informa al usuario que el email ya está en uso.
4.3 El sistema sugiere iniciar sesión o usar otro email.

4.a.1 Algún dato no pasa la validación (campo obligatorio vacío, región fuera del catálogo, contraseñas que no coinciden o email con formato inválido).
4.a.2 El sistema marca los campos con error e indica el motivo.
4.a.3 El sistema solicita corregir los datos y reintentar.

**Post condiciones**
La organización queda registrada en estado "pendiente" y no puede operar en la plataforma hasta ser aprobada (CU-02). No se emite sesión.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Los documentos de acreditación (certificados, registros) se pueden adjuntar posteriormente desde el perfil institucional (CU-14); la subida se realiza en dos pasos mediante URLs prefirmadas de almacenamiento.

---

## Identificador: CU-02

**Nombre**
Validar organización receptora

**Actores**
Administrador del Sistema

**Descripción**
El Administrador del Sistema revisa los antecedentes de una organización y la aprueba, rechaza (indicando un motivo), desactiva o reactiva.

**Pre condiciones**
1. El usuario debe corresponder al tipo Administrador del Sistema.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. Debe existir al menos una organización registrada (CU-01).

**Flujo principal**
1. El administrador accede al panel de gestión de organizaciones.
2. El sistema muestra el listado de organizaciones con filtro por estado (pendiente, activa, rechazada, inactiva) y los conteos por pestaña.
3. El administrador selecciona una organización pendiente.
4. El administrador revisa los datos y descarga los documentos de acreditación adjuntos.
5. El administrador selecciona la opción aprobar.
6. El sistema cambia el estado de la organización de "pendiente" a "activa" y registra el evento en el feed de actividad.

**Flujo alternativo**
5.1 El administrador decide rechazar la organización.
5.2 El administrador ingresa opcionalmente el motivo del rechazo.
5.3 El sistema cambia el estado a "rechazada", guarda el motivo y registra el evento.

5.a.1 El administrador desactiva una organización activa.
5.a.2 El sistema cambia el estado de "activa" a "inactiva".

5.b.1 El administrador reactiva una organización inactiva.
5.b.2 El sistema cambia el estado de "inactiva" a "activa".

**Post condiciones**
La organización queda en el estado resultante de la acción. Si fue aprobada, puede operar en la plataforma (gestionar su centro, necesidades y recepciones); si fue rechazada, el motivo queda visible en su perfil.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Las transiciones de estado son validadas por el sistema: solo se aprueba o rechaza una organización "pendiente", solo se desactiva una "activa" y solo se reactiva una "inactiva".

---

## Identificador: CU-03

**Nombre**
Gestionar lista de necesidades

**Actores**
Organización Receptora

**Descripción**
La Organización Receptora crea, actualiza o cierra manualmente las solicitudes de insumos que requiere su centro de acopio.

**Pre condiciones**
1. El usuario debe corresponder al tipo Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. La organización debe tener un centro de acopio registrado.

**Flujo principal**
1. La organización accede a la vista de gestión de necesidades de su centro.
2. El sistema muestra las necesidades existentes con sus cantidades (requerida, comprometida, recibida), urgencia, estado y cobertura.
3. La organización selecciona la opción crear necesidad.
4. La organización selecciona un insumo del catálogo global, indica la cantidad requerida y la urgencia (alta, media o baja).
5. La organización confirma la creación.
6. El sistema registra la necesidad en estado "activa", con cero comprometido y cero recibido, y la publica para los donantes.

**Flujo alternativo**
5.1 Ya existe una necesidad activa para el mismo insumo en el centro.
5.2 El sistema informa que no se puede duplicar y sugiere editar la necesidad existente.

3.a.1 La organización edita una necesidad existente (cantidad requerida y/o urgencia; el insumo no se puede cambiar).
3.a.2 Si la nueva cantidad requerida es menor a lo ya comprometido por donantes, el sistema rechaza el cambio e indica el mínimo permitido.
3.a.3 Si la necesidad está "completada" o "cerrada", el sistema informa que no es editable.

3.b.1 La organización cierra manualmente una necesidad activa.
3.b.2 El sistema cambia su estado a "cerrada" y deja de aceptar nuevos aportes.
3.b.3 El sistema cancela los ítems de aportes pendientes asociados a esa necesidad (motivo: cierre de necesidad), liberando el compromiso de los donantes.

**Post condiciones**
La lista de necesidades del centro queda actualizada y visible para los donantes en la consulta pública (CU-04) y en el mapa (CU-11).

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Una necesidad también puede pasar automáticamente a estado "completada" cuando los aportes comprometidos alcanzan el 100% de la meta (ver CU-05); ese cierre automático no cancela aportes pendientes.

---

## Identificador: CU-04

**Nombre**
Consultar necesidades

**Actores**
Donante Particular
Visitante

**Descripción**
El Donante Particular filtra y visualiza las listas de necesidades activas publicadas por las distintas organizaciones.

**Pre condiciones**
1. Deben existir centros de acopio con necesidades publicadas.

**Flujo principal**
1. El usuario accede al listado de centros de acopio.
2. El sistema muestra los centros con su organización, zona, cobertura y estado de saturación.
3. El usuario aplica filtros (región, tipo de centro, estado, emergencia asociada) u ordena por cobertura ascendente para ver primero los centros críticos.
4. El usuario selecciona un centro.
5. El sistema muestra el detalle del centro: dirección, horario, contacto de la organización, emergencia asociada y sus necesidades activas con cantidades, urgencia y cobertura.

**Flujo alternativo**
3.1 Ningún centro coincide con los filtros aplicados.
3.2 El sistema muestra el listado vacío e invita a modificar los filtros.

4.a.1 El centro seleccionado ya no existe.
4.a.2 El sistema informa que el centro no fue encontrado y regresa al listado.

**Post condiciones**
El usuario visualiza las necesidades activas del centro seleccionado y puede iniciar un aporte (CU-05).

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La consulta de centros y necesidades es pública (no requiere sesión); comprometer un aporte sí requiere haber iniciado sesión como donante.

---

## Identificador: CU-05

**Nombre**
Comprometer aporte

**Actores**
Donante Particular

**Descripción**
El Donante Particular selecciona una o más necesidades de un mismo centro, indica la cantidad a donar y confirma su intención de entrega, recibiendo un código de seguimiento.

**Pre condiciones**
1. El usuario debe corresponder al tipo Donante Particular.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. El centro seleccionado debe tener al menos una necesidad activa.

**Flujo principal**
1. El donante accede al formulario de donación de un centro.
2. El sistema muestra las necesidades activas del centro con la cantidad restante de cada una.
3. El donante selecciona una o más necesidades e indica la cantidad a aportar en cada una.
4. El donante confirma el aporte.
5. El sistema valida que todas las necesidades pertenezcan al mismo centro, estén activas y que las cantidades no sobrepasen la meta restante.
6. El sistema registra el aporte en estado "pendiente", reserva las cantidades comprometidas en cada necesidad y genera un código de seguimiento único (formato "CA-" más 8 caracteres).
7. El sistema muestra al donante el código de seguimiento para presentarlo al entregar físicamente la donación.

**Flujo alternativo**
5.1 Alguna cantidad sobrepasaría la meta de la necesidad (incluyendo compromisos concurrentes de otros donantes).
5.2 El sistema rechaza el aporte indicando la necesidad afectada.
5.3 El sistema actualiza las cantidades disponibles y sugiere ajustar el aporte.

5.a.1 Alguna necesidad seleccionada ya no está activa (fue cerrada o completada).
5.a.2 El sistema informa cuál necesidad no admite aportes y sugiere quitarla de la selección.

**Post condiciones**
El aporte queda registrado en estado "pendiente" con su código de seguimiento. Si alguna necesidad alcanza el 100% de su meta con este aporte, el sistema la marca automáticamente como "completada".

**Casos de uso incluidos**
CU-04 Consultar necesidades

**Casos de uso extendidos**
Ninguno

**Notas**
El compromiso solo reserva cupo (cantidad comprometida); el stock del centro se incrementa recién cuando la organización confirma la recepción física (CU-07). El sistema controla la concurrencia para impedir sobrestock entre donantes simultáneos.

---

## Identificador: CU-06

**Nombre**
Hacer seguimiento de aporte

**Actores**
Donante Particular

**Descripción**
El Donante Particular revisa el estado de sus aportes (pendiente, recibido o cancelado) mediante su código de seguimiento.

**Pre condiciones**
1. El usuario debe corresponder al tipo Donante Particular.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).

**Flujo principal**
1. El donante accede a la vista de seguimiento de sus aportes.
2. El sistema muestra el listado paginado de sus donaciones, de la más reciente a la más antigua.
3. El sistema muestra por cada aporte: código de seguimiento, centro y organización de destino, insumos y cantidades, fecha y estado (pendiente, recibido o cancelado).

**Flujo alternativo**
2.1 El donante no tiene aportes registrados.
2.2 El sistema muestra el listado vacío e invita a explorar los centros con necesidades activas.

**Post condiciones**
El donante conoce el estado actualizado de cada uno de sus aportes.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
CU-18 Cancelar aporte

**Notas**
Desde esta misma vista el donante puede cancelar un aporte que aún esté en estado "pendiente" (CU-18).

---

## Identificador: CU-07

**Nombre**
Confirmar recepción de aporte

**Actores**
Organización Receptora

**Descripción**
La Organización Receptora valida el código de seguimiento de un aporte entrante y confirma su recepción física, incorporándolo al stock del centro.

**Pre condiciones**
1. El usuario debe corresponder al tipo Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. La organización debe tener un centro registrado con aportes pendientes.

**Flujo principal**
1. La organización accede a la vista de recepciones de su centro.
2. El sistema muestra los aportes en estado "pendiente" dirigidos al centro, con sus insumos y cantidades.
3. La organización ingresa o verifica el código de seguimiento presentado por el donante.
4. La organización selecciona la opción confirmar recepción.
5. El sistema valida que el código exista y corresponda a un aporte de su centro.
6. El sistema marca la donación como "recibida", sella la fecha de confirmación e incrementa la cantidad recibida de cada necesidad involucrada.

**Flujo alternativo**
5.1 El código de seguimiento no existe.
5.2 El sistema informa que el código no es válido y sugiere verificarlo con el donante.

5.a.1 El código corresponde a un aporte de otro centro.
5.a.2 El sistema rechaza la operación indicando que el aporte no pertenece al centro.

5.b.1 El aporte ya fue confirmado anteriormente.
5.b.2 El sistema informa que la donación ya está registrada como recibida.

**Post condiciones**
La donación queda en estado "recibido", las necesidades involucradas suman la cantidad recibida y los insumos quedan disponibles en el stock del centro (CU-08). El donante ve el nuevo estado en su seguimiento (CU-06).

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Los ítems cancelados de un aporte (por el donante o por cierre de necesidad) no se contabilizan al confirmar la recepción.

---

## Identificador: CU-08

**Nombre**
Gestionar inventario

**Actores**
Organización Receptora

**Descripción**
La Organización Receptora consulta el stock disponible de su centro, calculado a partir de lo recibido menos lo distribuido.

**Pre condiciones**
1. El usuario debe corresponder al tipo Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. La organización debe tener un centro registrado.

**Flujo principal**
1. La organización accede a la vista de distribución e inventario de su centro.
2. El sistema calcula el stock disponible por insumo: total recibido en donaciones menos total registrado en lotes de salida.
3. El sistema muestra el stock disponible de cada insumo que haya registrado recepciones, junto al historial de lotes distribuidos.

**Flujo alternativo**
2.1 El centro aún no tiene donaciones recibidas.
2.2 El sistema muestra el inventario vacío e indica que el stock se genera al confirmar recepciones (CU-07).

**Post condiciones**
La organización conoce el stock disponible de cada insumo y puede registrar salidas de distribución (CU-15).

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
El stock es un valor derivado, no se almacena directamente: siempre refleja la diferencia entre lo recibido (CU-07) y lo distribuido (CU-15). Un insumo puede mostrar stock 0 si todo lo recibido ya fue despachado.

---

## Identificador: CU-09

**Nombre**
Gestionar cuenta de usuario

**Actores**
Donante Particular
Organización Receptora

**Descripción**
El Donante Particular o la Organización Receptora consulta y actualiza los datos de su perfil (nombre, contacto, correo).

**Pre condiciones**
1. El usuario debe corresponder al tipo Donante Particular u Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).

**Flujo principal**
1. El usuario accede a la vista de su perfil.
2. El sistema muestra los datos actuales de la cuenta (para el donante: nombre, apellido, email y fecha de registro; para la organización: datos de contacto).
3. El usuario modifica los campos editables.
4. El usuario selecciona la opción guardar.
5. El sistema valida los datos (campos obligatorios no vacíos, formato del email).
6. El sistema persiste los cambios y muestra el perfil actualizado.

**Flujo alternativo**
5.1 El nuevo email ya está en uso por otra cuenta.
5.2 El sistema rechaza el cambio informando que el email está ocupado.
5.3 El sistema sugiere ingresar un email distinto.

5.a.1 Algún campo obligatorio está vacío o el email tiene formato inválido.
5.a.2 El sistema marca los campos con error y solicita corregirlos.

**Post condiciones**
Los datos del perfil quedan actualizados; si cambió el email, las próximas sesiones se inician con el nuevo correo.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La gestión del perfil institucional completo de la organización (documentos de acreditación, datos del centro) se detalla en CU-14; este caso cubre los datos básicos de la cuenta.

---

## Identificador: CU-10

**Nombre**
Localizar centros de acopio cercanos

**Actores**
Donante Particular
Visitante

**Descripción**
El Donante Particular ubica en el mapa los centros de acopio a partir de su georreferenciación y filtros de zona.

**Pre condiciones**
1. Deben existir centros de acopio con coordenadas geográficas registradas.

**Flujo principal**
1. El usuario accede a la vista de mapa.
2. El sistema carga los centros de acopio con sus coordenadas (latitud y longitud).
3. El usuario aplica filtros de región o emergencia para acotar la búsqueda.
4. El sistema centra y ajusta el mapa a los centros que cumplen los filtros.
5. El usuario identifica los centros más cercanos a su ubicación.

**Flujo alternativo**
3.1 Ningún centro cumple los filtros aplicados.
3.2 El sistema muestra el mapa sin marcadores e invita a ampliar los filtros.

2.a.1 Un centro no tiene coordenadas registradas (la geocodificación de su dirección falló).
2.a.2 El sistema lo omite del mapa; el centro sigue disponible en el listado (CU-04).

**Post condiciones**
El usuario visualiza en el mapa los centros de acopio de la zona de interés y puede examinar cada uno (CU-11).

**Casos de uso incluidos**
CU-11 Visualizar información en el mapa

**Casos de uso extendidos**
Ninguno

**Notas**
Las coordenadas de un centro las entrega la organización al crearlo o editarlo; si no las indica, el sistema geocodifica automáticamente la dirección declarada (servicio de geocodificación externo).

---

## Identificador: CU-11

**Nombre**
Visualizar información en el mapa

**Actores**
Donante Particular
Visitante

**Descripción**
El Donante Particular visualiza los centros como marcadores en el mapa, con su estado de saturación y sus necesidades urgentes.

**Pre condiciones**
1. El usuario debe estar en la vista de mapa con centros cargados (CU-10).

**Flujo principal**
1. El sistema dibuja un marcador por cada centro georreferenciado, diferenciado según su estado de saturación (crítico, en capacidad o cerrado).
2. El usuario selecciona un marcador.
3. El sistema muestra la información del centro: nombre, organización, zona, cobertura de su meta y sus necesidades urgentes.
4. El usuario selecciona la opción ver detalle o donar.
5. El sistema lo dirige al detalle del centro (CU-04) o al formulario de aporte (CU-05).

**Flujo alternativo**
2.1 El usuario cierra la ficha del marcador sin seleccionar acciones.
2.2 El sistema mantiene la vista de mapa para seguir explorando.

**Post condiciones**
El usuario conoce el estado de saturación y las necesidades urgentes del centro seleccionado.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
El estado de saturación se deriva de la cobertura de las metas del centro: 0% crítico, entre 1% y 99% en capacidad, 100% cerrado. No es un dato ingresado manualmente.

---

## Identificador: CU-12

**Nombre**
Gestionar catálogo global de insumos

**Actores**
Administrador del Sistema

**Descripción**
El Administrador del Sistema da de alta, lista o da de baja los insumos estandarizados que las organizaciones usan para publicar sus necesidades.

**Pre condiciones**
1. El usuario debe corresponder al tipo Administrador del Sistema.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).

**Flujo principal**
1. El administrador accede a la vista de catálogo de insumos.
2. El sistema muestra los insumos activos con su nombre, categoría y unidad de medida.
3. El administrador selecciona la opción crear insumo.
4. El administrador ingresa el nombre, la categoría (del conjunto predefinido) y la unidad de medida.
5. El administrador confirma el alta.
6. El sistema registra el insumo y lo deja disponible para que las organizaciones publiquen necesidades con él.

**Flujo alternativo**
5.1 Ya existe un insumo activo con el mismo nombre (sin distinguir mayúsculas).
5.2 El sistema rechaza el alta informando el duplicado.

5.a.1 Existía un insumo con el mismo nombre dado de baja anteriormente.
5.a.2 El sistema lo reactiva conservando su identidad histórica, en lugar de crear uno nuevo.

3.b.1 El administrador da de baja un insumo del catálogo.
3.b.2 Si alguna organización tiene una necesidad activa con ese insumo, el sistema rechaza la baja indicando el conflicto.
3.b.3 Si no hay necesidades activas, el sistema lo desactiva (baja lógica); las necesidades históricas conservan su referencia.

**Post condiciones**
El catálogo queda actualizado; los listados de insumos disponibles para las organizaciones solo muestran insumos activos.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La baja es lógica (el insumo se marca inactivo, no se elimina), preservando la trazabilidad de necesidades y donaciones pasadas.

---

## Identificador: CU-13

**Nombre**
Visualizar métricas globales de la plataforma

**Actores**
Administrador del Sistema

**Descripción**
El Administrador del Sistema monitorea las estadísticas clave de campañas y el feed de actividad reciente de las organizaciones.

**Pre condiciones**
1. El usuario debe corresponder al tipo Administrador del Sistema.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).

**Flujo principal**
1. El administrador accede al panel principal de administración.
2. El sistema calcula y muestra las métricas globales: organizaciones por estado, centros operativos, donantes registrados, aportes registrados (excluyendo cancelados), entregas realizadas y emergencias activas.
3. El sistema muestra el feed de actividad reciente (organizaciones registradas, aprobadas y rechazadas), de lo más nuevo a lo más antiguo.

**Flujo alternativo**
3.1 No hay eventos de actividad registrados.
3.2 El sistema muestra el feed vacío.

**Post condiciones**
El administrador conoce el estado agregado de la plataforma y la actividad reciente de las organizaciones.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Las métricas se calculan en el momento de la consulta (agregados sobre los datos reales); el feed de actividad es un registro inmutable de eventos escrito al ocurrir cada acción (CU-01 y CU-02).

---

## Identificador: CU-14

**Nombre**
Gestionar perfil e información institucional

**Actores**
Organización Receptora

**Descripción**
La Organización Receptora actualiza sus datos de contacto y administra los documentos de acreditación de su centro.

**Pre condiciones**
1. El usuario debe corresponder al tipo Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).

**Flujo principal**
1. La organización accede a la vista de su perfil institucional.
2. El sistema muestra la identidad de la organización (nombre, tipo, RUT, estado, fecha de registro), sus datos de contacto y los documentos de acreditación adjuntos.
3. La organización edita los datos de contacto: nombre del contacto, email, teléfono y región.
4. La organización selecciona la opción guardar.
5. El sistema valida los datos y persiste los cambios.

**Flujo alternativo**
5.1 El nuevo email ya está en uso por otra cuenta.
5.2 El sistema rechaza el cambio e informa el conflicto.

3.a.1 La organización adjunta un documento de acreditación.
3.a.2 El sistema entrega una URL de subida segura, la organización sube el archivo y el sistema registra el documento.
3.a.3 El documento queda disponible para descarga por la propia organización y por el administrador (CU-02).

**Post condiciones**
El perfil institucional queda actualizado; los documentos adjuntos quedan disponibles para la revisión de antecedentes del administrador.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La identidad de la organización (nombre, tipo, RUT) no es editable desde el perfil; si la organización fue rechazada, el sistema muestra el motivo del rechazo registrado por el administrador.

---

## Identificador: CU-15

**Nombre**
Registrar lotes de distribución y despachos

**Actores**
Organización Receptora

**Descripción**
La Organización Receptora registra la salida de insumos hacia terreno o beneficiarios, rebajando el stock disponible del centro.

**Pre condiciones**
1. El usuario debe corresponder al tipo Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. El centro debe tener stock disponible del insumo a despachar (CU-08).

**Flujo principal**
1. La organización accede a la vista de distribución de su centro.
2. La organización selecciona la opción registrar salida.
3. La organización selecciona el insumo, ingresa la cantidad, el tipo de salida (enviado a terreno o entregado a beneficiario) y el destino.
4. La organización confirma el registro.
5. El sistema valida que la cantidad no supere el stock disponible y que el tipo de salida corresponda al tipo de centro (un centro de acopio envía a terreno; un punto de distribución entrega a beneficiarios; un centro mixto puede ambas).
6. El sistema registra el lote de salida y rebaja el stock disponible del insumo.

**Flujo alternativo**
5.1 La cantidad ingresada supera el stock disponible del insumo.
5.2 El sistema rechaza el registro indicando el máximo disponible.
5.3 El sistema sugiere ajustar la cantidad.

5.a.1 El tipo de salida no está permitido para el tipo de centro.
5.a.2 El sistema rechaza el registro e informa los tipos de salida válidos.

**Post condiciones**
El lote queda registrado en el historial de despachos del centro y el stock disponible refleja la rebaja (CU-08).

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Los lotes son registros inmutables (no se editan ni eliminan), lo que preserva la trazabilidad de lo distribuido. El sistema controla la concurrencia entre recepciones y despachos simultáneos.

---

## Identificador: CU-16

**Nombre**
Registrar donante particular

**Actores**
Visitante

**Descripción**
El Visitante ingresa sus datos personales para crear una cuenta de donante e inicia sesión de inmediato en la plataforma.

**Pre condiciones**
1. El usuario no debe tener una sesión iniciada.
2. El email no debe estar registrado previamente en la plataforma.

**Flujo principal**
1. El visitante accede al formulario de registro de donante.
2. El visitante ingresa su nombre, apellido, email y contraseña.
3. El visitante selecciona la opción registrarse.
4. El sistema valida los datos (campos obligatorios, formato del email).
5. El sistema crea la cuenta con rol de donante y la contraseña protegida (hash).
6. El sistema emite la sesión de inmediato y dirige al donante a su panel principal.

**Flujo alternativo**
4.1 El email ya está registrado en la plataforma.
4.2 El sistema informa que el email ya está en uso.
4.3 El sistema sugiere iniciar sesión (CU-17) o usar otro email.

4.a.1 Algún dato no pasa la validación.
4.a.2 El sistema marca los campos con error y solicita corregirlos.

**Post condiciones**
La cuenta de donante queda creada y con sesión activa; el donante puede consultar necesidades (CU-04) y comprometer aportes (CU-05) inmediatamente.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
A diferencia del registro de organización (CU-01), el donante no requiere aprobación del administrador: su cuenta queda operativa al instante.

---

## Identificador: CU-17

**Nombre**
Iniciar sesión

**Actores**
Donante Particular
Organización Receptora
Administrador del Sistema

**Descripción**
El Usuario ingresa sus credenciales para autenticarse y obtener acceso a las funciones correspondientes a su rol.

**Pre condiciones**
1. El usuario debe tener una cuenta registrada en la plataforma (CU-01 o CU-16, o la cuenta de administrador provista por el sistema).

**Flujo principal**
1. El usuario accede al formulario de inicio de sesión.
2. El usuario ingresa su email y contraseña.
3. El usuario selecciona la opción ingresar.
4. El sistema verifica las credenciales contra las cuentas registradas.
5. El sistema emite un token de sesión que identifica al usuario y su rol (donante, organización o administrador).
6. El sistema dirige al usuario al panel correspondiente a su rol.

**Flujo alternativo**
4.1 El email no existe o la contraseña no coincide.
4.2 El sistema muestra un mensaje genérico de credenciales incorrectas (sin revelar cuál dato falló).
4.3 El sistema sugiere reintentar.

4.a.1 El usuario supera el límite de intentos permitidos por minuto.
4.a.2 El sistema bloquea temporalmente nuevos intentos desde esa conexión para prevenir ataques de fuerza bruta.

**Post condiciones**
El usuario queda autenticado con una sesión activa; el sistema autoriza cada operación posterior según el rol contenido en el token.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La sesión se rehidrata al recargar la aplicación validando el token contra el servidor. Una organización en estado "pendiente" o "rechazada" puede autenticarse, pero sus funciones operativas quedan sujetas a la aprobación del administrador (CU-02).

---

## Identificador: CU-18

**Nombre**
Cancelar aporte

**Actores**
Donante Particular

**Descripción**
El Donante Particular anula un aporte pendiente, liberando el cupo comprometido y reabriendo la necesidad si estaba completada.

**Pre condiciones**
1. El usuario debe corresponder al tipo Donante Particular.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. El aporte a cancelar debe pertenecer al donante y estar en estado "pendiente".

**Flujo principal**
1. El donante accede a la vista de seguimiento de sus aportes (CU-06).
2. El donante selecciona un aporte en estado "pendiente".
3. El donante selecciona la opción cancelar y confirma la acción.
4. El sistema anula todos los ítems del aporte (motivo: cancelación del donante), conservando el registro para trazabilidad.
5. El sistema revierte las cantidades comprometidas en cada necesidad involucrada.
6. El sistema marca la donación como "cancelada" y, si alguna necesidad había quedado "completada" gracias a este aporte, la reabre a estado "activa".

**Flujo alternativo**
3.1 El aporte ya fue recibido por la organización o ya estaba cancelado.
3.2 El sistema rechaza la operación e informa el estado actual del aporte.

**Post condiciones**
El aporte queda en estado "cancelada", el cupo liberado vuelve a estar disponible para otros donantes y las necesidades reabiertas vuelven a aceptar aportes.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La cancelación es lógica (los ítems se marcan inactivos sin borrarse), preservando el código de seguimiento y la trazabilidad. Un aporte también puede quedar parcialmente anulado si la organización cierra manualmente una de las necesidades involucradas (CU-03); en ese caso la donación pasa a "cancelada" solo si todos sus ítems quedan anulados.

---

## Identificador: CU-19

**Nombre**
Gestionar emergencias

**Actores**
Administrador del Sistema

**Descripción**
El Administrador del Sistema crea, lista y cierra las emergencias que agrupan a los centros de acopio de la plataforma.

**Pre condiciones**
1. El usuario debe corresponder al tipo Administrador del Sistema.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).

**Flujo principal**
1. El administrador accede a la vista de gestión de emergencias.
2. El sistema muestra las emergencias activas y cerradas (historial), con su tipo, zona, fecha de inicio, total de centros vinculados y cobertura agregada.
3. El administrador selecciona la opción crear emergencia.
4. El administrador ingresa el nombre, el tipo (terremoto, incendio, aluvión u otro), la zona afectada y la fecha de inicio.
5. El administrador confirma la creación.
6. El sistema registra la emergencia en estado "activa", sin centros vinculados.

**Flujo alternativo**
5.1 Algún dato no pasa la validación (campos vacíos o tipo fuera del conjunto permitido).
5.2 El sistema marca los campos con error y solicita corregirlos.

3.a.1 El administrador cierra una emergencia activa.
3.a.2 El sistema cambia su estado a "cerrada" sin desvincular los centros (el vínculo se conserva como histórico).
3.a.3 Si la emergencia ya estaba cerrada, el sistema informa el conflicto.

**Post condiciones**
La emergencia queda disponible en el estado resultante. Solo las emergencias activas admiten nuevos vínculos de centros (CU-20) y aparecen en los filtros públicos del donante.

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
La cobertura y el total de centros de una emergencia son valores derivados de sus centros vinculados; el administrador no asigna centros directamente (eso lo hace cada organización, CU-20).

---

## Identificador: CU-20

**Nombre**
Vincular centro a emergencia

**Actores**
Organización Receptora

**Descripción**
La Organización Receptora asocia su centro de acopio a una emergencia activa o lo desvincula de ella.

**Pre condiciones**
1. El usuario debe corresponder al tipo Organización Receptora.
2. El usuario debe haber iniciado sesión a través de la plataforma web (CU-17).
3. La organización debe tener un centro de acopio registrado.
4. Debe existir al menos una emergencia activa (CU-19) para poder vincular.

**Flujo principal**
1. La organización accede al formulario de edición de su centro de acopio.
2. El sistema muestra los datos del centro y el selector de emergencias activas.
3. La organización selecciona la emergencia a la que responde su centro.
4. La organización guarda los cambios.
5. El sistema valida que la emergencia exista y esté activa.
6. El sistema vincula el centro a la emergencia; el centro pasa a contar en el total y la cobertura agregada de esa emergencia.

**Flujo alternativo**
3.1 La organización selecciona la opción sin emergencia.
3.2 El sistema desvincula el centro de la emergencia que tenía asociada.

5.a.1 La emergencia seleccionada no existe o ya fue cerrada.
5.a.2 El sistema rechaza el vínculo e informa que solo se puede vincular a una emergencia activa.

**Post condiciones**
El centro queda vinculado (o desvinculado) a la emergencia; el vínculo se refleja en los filtros y agregados que ven los donantes (CU-04, CU-10, CU-11) y el administrador (CU-19).

**Casos de uso incluidos**
Ninguno

**Casos de uso extendidos**
Ninguno

**Notas**
Cada organización solo vincula su propio centro (el administrador no asigna centros ajenos). Si la emergencia se cierra después (CU-19), el vínculo se conserva como registro histórico.
