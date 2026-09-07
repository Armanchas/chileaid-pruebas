# Casos de Prueba — Chile Aid

Casos de prueba derivados de los casos de uso especificados en `CU.md`. Para cada caso de uso seleccionado se define un caso **exitoso**, uno **negativo** y uno de **límite**. Nomenclatura: `TC-CUxx-01` (exitoso), `TC-CUxx-02` (negativo), `TC-CUxx-03` (límite).

Los datos de prueba referencian las cuentas del seed de desarrollo: administrador `admin@chileaid.cl` / `admin1234`, organización activa `bomberos.losangeles@chileaid.cl` / `org1234`, donante `pedro.soto@gmail.com` / `donante1234`.

---

## CU-01 — Registrar organización receptora

### TC-CU01-01

**Registro de organización exitoso**

**Propósito**
Verificar que una organización puede registrarse con datos válidos y queda en estado pendiente de aprobación.

**Prioridad**
Alta

**Datos de prueba**
Nombre: "Fundación Manos Unidas"; tipo de centro: centro de acopio; RUT: 76.543.210-9; región: "Biobío"; dirección: "Av. Siempre Viva 742"; contacto: "Laura Méndez"; email nuevo no registrado: `nueva.org@chileaid.cl`; teléfono: +56987654321; contraseña y confirmación: `secreta123`.

**Pasos detallados**
1. El usuario accede al formulario de registro de organización.
2. El usuario completa los nueve campos del formulario con los datos de prueba.
3. El usuario presiona "Registrar".

**Resultados esperados**
El sistema crea la cuenta representante y la organización en estado "pendiente", informa que la solicitud quedó pendiente de aprobación y no inicia sesión. La organización aparece en la pestaña "pendiente" del panel del administrador.

### TC-CU01-02

**Registro rechazado por email duplicado**

**Propósito**
Verificar que el sistema impide registrar una organización con un email ya existente en la plataforma.

**Prioridad**
Alta

**Datos de prueba**
Formulario completo y válido, pero con el email ya registrado `bomberos.losangeles@chileaid.cl`.

**Pasos detallados**
1. El usuario accede al formulario de registro de organización.
2. El usuario completa todos los campos usando el email ya registrado.
3. El usuario presiona "Registrar".

**Resultados esperados**
El sistema rechaza el registro e informa que el email ya está en uso (conflicto 409). No se crea ninguna cuenta ni organización nueva.

### TC-CU01-03

**Registro en el límite: RUT omitido y región en el borde del catálogo**

**Propósito**
Verificar el comportamiento con los campos en sus valores límite: el RUT (único campo opcional) omitido y una región válida escrita exactamente como figura en el catálogo nacional, contra una variante que no figura.

**Prioridad**
Media

**Datos de prueba**
Caso A: formulario válido sin RUT y región "Magallanes y de la Antártica Chilena" (valor exacto del catálogo). Caso B: mismo formulario con región "Magallanes" (valor fuera del catálogo).

**Pasos detallados**
1. El usuario accede al formulario de registro de organización.
2. El usuario completa el formulario del caso A, dejando el RUT vacío, y presiona "Registrar".
3. El usuario repite el registro con otro email usando los datos del caso B y presiona "Registrar".

**Resultados esperados**
Caso A: el registro se acepta (201) y la organización queda "pendiente" con RUT nulo. Caso B: el sistema rechaza el registro por validación (422) indicando que la región no pertenece al catálogo.

---

## CU-03 — Gestionar lista de necesidades

### TC-CU03-01

**Creación de necesidad exitosa**

**Propósito**
Verificar que la organización puede publicar una nueva necesidad de un insumo del catálogo.

**Prioridad**
Alta

**Datos de prueba**
Sesión de `bomberos.losangeles@chileaid.cl` (organización activa con centro registrado); insumo del catálogo sin necesidad activa en el centro (ej. "Pañales"); cantidad requerida: 200; urgencia: alta.

**Pasos detallados**
1. La organización inicia sesión y accede a la gestión de necesidades de su centro.
2. La organización presiona "Crear necesidad".
3. La organización selecciona el insumo "Pañales" del catálogo, ingresa cantidad requerida 200 y urgencia "alta".
4. La organización confirma la creación.

**Resultados esperados**
El sistema registra la necesidad en estado "activa" con cantidad comprometida 0, recibida 0 y cobertura 0%. La necesidad aparece de inmediato en la consulta pública del centro (CU-04).

### TC-CU03-02

**Creación rechazada por insumo duplicado activo**

**Propósito**
Verificar que el sistema impide tener dos necesidades activas del mismo insumo en un mismo centro.

**Prioridad**
Alta

**Datos de prueba**
Sesión de la organización; insumo "Agua embotellada", que ya tiene una necesidad activa en el centro (datos del seed).

**Pasos detallados**
1. La organización accede a la gestión de necesidades.
2. La organización presiona "Crear necesidad" y selecciona "Agua embotellada", cantidad 100, urgencia media.
3. La organización confirma la creación.

**Resultados esperados**
El sistema rechaza la creación (conflicto 409) e informa que ya existe una necesidad activa para ese insumo, sugiriendo editarla en lugar de duplicarla.

### TC-CU03-03

**Edición en el límite de lo comprometido**

**Propósito**
Verificar que al editar una necesidad, la cantidad requerida puede bajar exactamente hasta lo ya comprometido, pero no por debajo.

**Prioridad**
Alta

**Datos de prueba**
Necesidad activa con cantidad requerida 500 y cantidad comprometida 200 (ej. "Agua embotellada" del seed).

**Pasos detallados**
1. La organización accede a la gestión de necesidades y edita la necesidad de prueba.
2. La organización cambia la cantidad requerida a 200 (exactamente lo comprometido) y guarda.
3. La organización vuelve a editar, cambia la cantidad requerida a 199 y guarda.

**Resultados esperados**
Paso 2: el sistema acepta el cambio; la cobertura queda en 100% y la necesidad **permanece activa** (el paso automático a "completada" solo ocurre al comprometer aportes, no al editar la meta). Paso 3: el sistema rechaza el cambio (422) indicando que la cantidad no puede ser menor a lo ya comprometido (200).

---

## CU-04 — Consultar necesidades

### TC-CU04-01

**Consulta de necesidades exitosa**

**Propósito**
Verificar que un donante puede filtrar centros y ver las necesidades activas de un centro.

**Prioridad**
Alta

**Datos de prueba**
Centros del seed con necesidades activas; filtro región "Bío Bío".

**Pasos detallados**
1. El usuario accede al listado de centros de acopio.
2. El usuario aplica el filtro de región "Bío Bío".
3. El usuario selecciona el "Centro de Acopio Bomberos Los Ángeles".

**Resultados esperados**
El listado muestra solo los centros de la región filtrada, con su cobertura y estado de saturación. El detalle del centro muestra dirección, horario, contacto de la organización y sus necesidades activas con cantidades, urgencia y cobertura.

### TC-CU04-02

**Consulta de centro inexistente**

**Propósito**
Verificar que el sistema maneja correctamente el acceso al detalle de un centro que no existe.

**Prioridad**
Media

**Datos de prueba**
Identificador de centro válido en formato pero inexistente en la base (UUID aleatorio).

**Pasos detallados**
1. El usuario accede directamente a la URL de detalle de un centro con un identificador inexistente.

**Resultados esperados**
El sistema informa que el centro no fue encontrado (404) y ofrece regresar al listado; la aplicación no queda en un estado de error.

### TC-CU04-03

**Consulta límite: filtros sin resultados**

**Propósito**
Verificar el comportamiento del listado cuando la combinación de filtros no coincide con ningún centro.

**Prioridad**
Baja

**Datos de prueba**
Combinación de filtros sin coincidencias (ej. región "Arica y Parinacota" + estado "cerrado", sin centros del seed).

**Pasos detallados**
1. El usuario accede al listado de centros de acopio.
2. El usuario aplica la combinación de filtros sin coincidencias.

**Resultados esperados**
El sistema devuelve una lista vacía (200 con `[]`, no un error) y la vista muestra el estado vacío invitando a modificar los filtros.

---

## CU-05 — Comprometer aporte

### TC-CU05-01

**Compromiso de aporte exitoso**

**Propósito**
Verificar que un donante puede comprometer un aporte a varias necesidades de un mismo centro y recibe su código de seguimiento.

**Prioridad**
Alta

**Datos de prueba**
Sesión de `pedro.soto@gmail.com`; centro con dos necesidades activas con cupo disponible; cantidades dentro del restante de cada una (ej. 50 litros de agua y 20 kilos de arroz).

**Pasos detallados**
1. El donante inicia sesión y accede al formulario de donación del centro.
2. El donante selecciona las dos necesidades e ingresa las cantidades de prueba.
3. El donante confirma el aporte.

**Resultados esperados**
El sistema registra la donación en estado "pendiente", muestra un código de seguimiento con formato "CA-" más 8 caracteres, y la cantidad comprometida de cada necesidad aumenta en lo aportado. El aporte aparece en el seguimiento del donante (CU-06) y en las recepciones pendientes de la organización (CU-07).

### TC-CU05-02

**Compromiso rechazado por sobrepasar la meta**

**Propósito**
Verificar que el sistema impide comprometer una cantidad mayor al cupo restante de una necesidad.

**Prioridad**
Alta

**Datos de prueba**
Necesidad activa con cantidad requerida 500 y comprometida 200 (restante: 300); cantidad a aportar: 301.

**Pasos detallados**
1. El donante accede al formulario de donación del centro.
2. El donante selecciona la necesidad de prueba e ingresa cantidad 301.
3. El donante confirma el aporte.

**Resultados esperados**
El sistema rechaza el aporte (422) indicando la necesidad afectada, no registra ninguna donación y no altera la cantidad comprometida. El sistema sugiere ajustar la cantidad al restante disponible.

### TC-CU05-03

**Compromiso límite: cantidad exactamente igual al restante**

**Propósito**
Verificar que aportar exactamente el cupo restante se acepta y dispara el cierre automático de la necesidad al 100%.

**Prioridad**
Alta

**Datos de prueba**
Necesidad activa con requerida 500 y comprometida 200 (restante: 300); cantidad a aportar: 300. Caso de contraste: cantidad 0.

**Pasos detallados**
1. El donante accede al formulario de donación e ingresa cantidad 300 en la necesidad de prueba.
2. El donante confirma el aporte.
3. El donante intenta un nuevo aporte a cualquier necesidad con cantidad 0 y confirma.

**Resultados esperados**
Paso 2: el sistema acepta el aporte, la cobertura llega a 100% y la necesidad pasa automáticamente a "completada", dejando de aceptar nuevos aportes. Paso 3: el sistema rechaza la cantidad 0 por validación (422, la cantidad debe ser mayor que cero).

---

## CU-07 — Confirmar recepción de aporte

### TC-CU07-01

**Confirmación de recepción exitosa**

**Propósito**
Verificar que la organización puede confirmar la recepción física de un aporte mediante su código de seguimiento.

**Prioridad**
Alta

**Datos de prueba**
Sesión de la organización dueña del centro; donación en estado "pendiente" dirigida a su centro, con código de seguimiento conocido (generado en TC-CU05-01).

**Pasos detallados**
1. La organización inicia sesión y accede a la vista de recepciones.
2. El sistema muestra el aporte pendiente con sus insumos y cantidades.
3. La organización ingresa el código de seguimiento presentado por el donante.
4. La organización presiona "Confirmar recepción".

**Resultados esperados**
El sistema marca la donación como "recibida", sella la fecha de confirmación e incrementa la cantidad recibida de cada necesidad involucrada. El donante ve el estado "recibido" en su seguimiento y los insumos quedan disponibles en el stock del centro (CU-08).

### TC-CU07-02

**Confirmación rechazada por código inválido o ajeno**

**Propósito**
Verificar que el sistema rechaza códigos inexistentes y códigos de aportes dirigidos a otro centro.

**Prioridad**
Alta

**Datos de prueba**
Caso A: código inexistente "CA-00000000". Caso B: código válido de una donación dirigida al centro de otra organización.

**Pasos detallados**
1. La organización accede a la vista de recepciones.
2. La organización ingresa el código del caso A y presiona "Confirmar recepción".
3. La organización ingresa el código del caso B y presiona "Confirmar recepción".

**Resultados esperados**
Caso A: el sistema informa que el código no es válido (404) y sugiere verificarlo con el donante. Caso B: el sistema rechaza la operación (403) indicando que el aporte no pertenece al centro. En ninguno de los dos casos se modifica donación o necesidad alguna.

### TC-CU07-03

**Confirmación límite: doble confirmación del mismo código**

**Propósito**
Verificar que un aporte ya confirmado no puede confirmarse por segunda vez (idempotencia del cierre).

**Prioridad**
Alta

**Datos de prueba**
Código de seguimiento de una donación ya confirmada (resultado de TC-CU07-01).

**Pasos detallados**
1. La organización accede a la vista de recepciones.
2. La organización ingresa el código ya confirmado y presiona "Confirmar recepción".

**Resultados esperados**
El sistema rechaza la operación (409) informando que la donación ya está registrada como recibida. Las cantidades recibidas de las necesidades no se incrementan por segunda vez.

---

## CU-08 — Gestionar inventario

### TC-CU08-01

**Consulta de stock exitosa**

**Propósito**
Verificar que la organización ve el stock disponible calculado como lo recibido menos lo distribuido.

**Prioridad**
Alta

**Datos de prueba**
Centro con una recepción confirmada de 300 litros de agua (TC-CU07-01) y un lote de salida previo de 100 litros.

**Pasos detallados**
1. La organización inicia sesión y accede a la vista de distribución e inventario.

**Resultados esperados**
El sistema muestra el insumo "Agua embotellada" con stock disponible 200 (300 recibidos − 100 distribuidos), junto al historial de lotes despachados. Solo aparecen insumos con recepciones registradas.

### TC-CU08-02

**Acceso al inventario denegado por rol**

**Propósito**
Verificar que el inventario del centro solo es accesible para la organización dueña, no para donantes.

**Prioridad**
Media

**Datos de prueba**
Sesión de donante `pedro.soto@gmail.com`.

**Pasos detallados**
1. El donante inicia sesión.
2. El donante intenta acceder directamente al recurso de stock de la organización (URL o petición directa al endpoint).

**Resultados esperados**
El sistema deniega el acceso (403) indicando que no tiene permisos para la acción; no se expone información de stock de ningún centro.

### TC-CU08-03

**Inventario límite: stock exactamente en cero**

**Propósito**
Verificar que un insumo cuyo total recibido fue completamente distribuido se muestra con stock 0 y no permite nuevos despachos.

**Prioridad**
Media

**Datos de prueba**
Insumo con 300 unidades recibidas y lotes de salida que suman 300 (despacho total, ver TC-CU15/CU-08).

**Pasos detallados**
1. La organización registra un lote de salida por el total restante del insumo (dejando el stock en 0).
2. La organización consulta la vista de inventario.
3. La organización intenta registrar un nuevo lote de 1 unidad del mismo insumo.

**Resultados esperados**
Paso 2: el insumo aparece listado con cantidad disponible 0 (no desaparece del inventario). Paso 3: el sistema rechaza el despacho (422) indicando que el stock es insuficiente.

---

## CU-17 — Iniciar sesión

### TC-CU17-01

**Inicio de sesión exitoso**

**Propósito**
Verificar que el usuario puede ingresar al sistema con credenciales válidas y es dirigido al panel de su rol.

**Prioridad**
Alta

**Datos de prueba**
Donante registrado: `pedro.soto@gmail.com` / `donante1234`. Verificación cruzada con `admin@chileaid.cl` / `admin1234` y `bomberos.losangeles@chileaid.cl` / `org1234`.

**Pasos detallados**
1. El sistema muestra el formulario de inicio de sesión.
2. El usuario ingresa su email.
3. El usuario ingresa su contraseña.
4. El usuario presiona "Iniciar sesión".

**Resultados esperados**
El sistema autentica al usuario, emite el token de sesión con su rol y lo redirige a la pantalla principal según ese rol: el donante a su panel de donante, la organización al panel de su centro y el administrador al panel de administración.

### TC-CU17-02

**Inicio de sesión rechazado por credenciales incorrectas**

**Propósito**
Verificar que el sistema rechaza credenciales inválidas con un mensaje genérico que no revela cuál dato falló.

**Prioridad**
Alta

**Datos de prueba**
Caso A: email registrado `pedro.soto@gmail.com` con contraseña incorrecta `xxxxxx`. Caso B: email no registrado `noexiste@gmail.com` con cualquier contraseña.

**Pasos detallados**
1. El usuario accede al formulario de inicio de sesión.
2. El usuario ingresa las credenciales del caso A y presiona "Iniciar sesión".
3. El usuario ingresa las credenciales del caso B y presiona "Iniciar sesión".

**Resultados esperados**
En ambos casos el sistema responde 401 con el mismo mensaje genérico ("Email o contraseña incorrectos"), sin distinguir si el email existe o no (previene enumeración de cuentas). No se emite token ni se inicia sesión.

### TC-CU17-03

**Inicio de sesión límite: sexto intento dentro del minuto**

**Propósito**
Verificar que el límite de 5 intentos por minuto por conexión bloquea temporalmente el sexto intento.

**Prioridad**
Media

**Datos de prueba**
Credenciales cualesquiera (válidas o no) enviadas 6 veces consecutivas desde la misma IP en menos de un minuto.

**Pasos detallados**
1. El usuario envía 5 intentos de inicio de sesión consecutivos dentro del mismo minuto.
2. El usuario envía un sexto intento antes de cumplirse el minuto.
3. El usuario espera a que expire la ventana y reintenta con credenciales válidas.

**Resultados esperados**
Los primeros 5 intentos se procesan normalmente (éxito o 401 según credenciales). El sexto intento es bloqueado por el límite de tasa (429) sin evaluar las credenciales. Pasada la ventana, el intento con credenciales válidas vuelve a autenticarse con normalidad.

---

## CU-19 — Gestionar emergencias

### TC-CU19-01

**Creación de emergencia exitosa**

**Propósito**
Verificar que el administrador puede crear una emergencia que nace activa y sin centros vinculados.

**Prioridad**
Alta

**Datos de prueba**
Sesión de `admin@chileaid.cl`; nombre: "Incendio forestal Valparaíso 2026"; tipo: incendio; zona: "Valparaíso"; fecha de inicio: 2026-07-05.

**Pasos detallados**
1. El administrador inicia sesión y accede a la gestión de emergencias.
2. El administrador presiona "Crear emergencia".
3. El administrador ingresa nombre, tipo, zona y fecha de inicio.
4. El administrador confirma la creación.

**Resultados esperados**
El sistema registra la emergencia en estado "activa", con 0 centros vinculados y cobertura 0. La emergencia aparece en el listado del administrador y queda disponible para que las organizaciones vinculen sus centros (CU-20).

### TC-CU19-02

**Creación rechazada por tipo inválido**

**Propósito**
Verificar que el sistema rechaza una emergencia con un tipo fuera del conjunto permitido (terremoto, incendio, aluvión, otro).

**Prioridad**
Media

**Datos de prueba**
Formulario con nombre y zona válidos, pero tipo "tsunami" (fuera del enum) o nombre vacío.

**Pasos detallados**
1. El administrador accede a la gestión de emergencias y presiona "Crear emergencia".
2. El administrador ingresa los datos de prueba con el tipo inválido.
3. El administrador confirma la creación.

**Resultados esperados**
El sistema rechaza la creación por validación (422) indicando el campo con error; no se registra ninguna emergencia.

### TC-CU19-03

**Cierre límite: cerrar una emergencia ya cerrada**

**Propósito**
Verificar la transición de estado en su borde: el cierre solo aplica una vez y conserva los vínculos históricos.

**Prioridad**
Media

**Datos de prueba**
Emergencia activa con al menos un centro vinculado (seed o TC-CU20-01).

**Pasos detallados**
1. El administrador accede a la gestión de emergencias y cierra la emergencia de prueba.
2. El administrador verifica el listado de centros vinculados de la emergencia cerrada.
3. El administrador intenta cerrar la misma emergencia por segunda vez.

**Resultados esperados**
Paso 1: la emergencia pasa de "activa" a "cerrada". Paso 2: los centros conservan su vínculo como registro histórico (no se desvinculan en cascada). Paso 3: el sistema rechaza el segundo cierre (409) informando que la emergencia ya estaba cerrada.

---

## CU-20 — Vincular centro a emergencia

### TC-CU20-01

**Vinculación de centro exitosa**

**Propósito**
Verificar que la organización puede asociar su centro a una emergencia activa.

**Prioridad**
Alta

**Datos de prueba**
Sesión de organización activa con centro registrado y sin emergencia asociada; emergencia activa existente (del seed o TC-CU19-01).

**Pasos detallados**
1. La organización inicia sesión y accede a la edición de su centro.
2. La organización selecciona la emergencia activa en el selector de emergencias.
3. La organización guarda los cambios.

**Resultados esperados**
El sistema vincula el centro a la emergencia. El centro pasa a contar en el total de centros y en la cobertura agregada de esa emergencia, y aparece al filtrar por ella en el listado y el mapa del donante.

### TC-CU20-02

**Vinculación rechazada a emergencia cerrada**

**Propósito**
Verificar que el sistema impide vincular un centro a una emergencia que ya fue cerrada.

**Prioridad**
Alta

**Datos de prueba**
Sesión de la organización; identificador de una emergencia en estado "cerrada" (TC-CU19-03).

**Pasos detallados**
1. La organización accede a la edición de su centro.
2. La organización intenta guardar el centro con la emergencia cerrada como vínculo (vía petición directa, ya que el selector solo ofrece activas).

**Resultados esperados**
El sistema rechaza el vínculo (422) informando que solo se puede vincular a una emergencia activa; el centro conserva su vínculo anterior (o ninguno).

### TC-CU20-03

**Vinculación límite: desvincular el centro (valor nulo)**

**Propósito**
Verificar el valor límite del campo: enviar "sin emergencia" desvincula el centro sin afectar el resto de sus datos.

**Prioridad**
Media

**Datos de prueba**
Centro actualmente vinculado a una emergencia activa (resultado de TC-CU20-01).

**Pasos detallados**
1. La organización accede a la edición de su centro.
2. La organización selecciona la opción "Sin emergencia" en el selector.
3. La organización guarda los cambios.

**Resultados esperados**
El sistema desvincula el centro (emergencia nula) conservando intactos sus demás datos y necesidades. La emergencia deja de contar ese centro en su total y su cobertura agregada; el centro deja de aparecer al filtrar por esa emergencia.

---

## CU-11 — Visualizar información en el mapa

### TC-CU11-01

**Visualización de marcadores exitosa**

**Propósito**
Verificar que los centros georreferenciados se muestran como marcadores con su estado de saturación y necesidades urgentes.

**Prioridad**
Alta

**Datos de prueba**
Centros del seed con coordenadas registradas y necesidades activas de urgencia alta.

**Pasos detallados**
1. El usuario accede a la vista de mapa.
2. El sistema carga los centros georreferenciados.
3. El usuario selecciona el marcador de un centro.

**Resultados esperados**
El mapa dibuja un marcador por cada centro con coordenadas, diferenciado según su estado (crítico, en capacidad o cerrado). Al seleccionar el marcador se muestra nombre, organización, zona, cobertura y las necesidades urgentes del centro, con acceso al detalle (CU-04) y al formulario de aporte (CU-05).

### TC-CU11-02

**Centro sin coordenadas omitido del mapa**

**Propósito**
Verificar que un centro sin georreferenciación no rompe el mapa: se omite de los marcadores pero sigue disponible en el listado.

**Prioridad**
Media

**Datos de prueba**
Centro creado con una dirección que el servicio de geocodificación no resuelve (coordenadas nulas).

**Pasos detallados**
1. La organización crea su centro con una dirección no geocodificable y sin ingresar coordenadas manuales.
2. El usuario accede a la vista de mapa.
3. El usuario accede al listado de centros (CU-04).

**Resultados esperados**
El mapa se renderiza sin errores y el centro sin coordenadas no aparece como marcador. En el listado de centros el mismo centro sí aparece con toda su información.

### TC-CU11-03

**Visualización límite: estados de saturación en los bordes de cobertura**

**Propósito**
Verificar que el marcador refleja el estado derivado en los valores límite de cobertura: 0%, 1% y 100%.

**Prioridad**
Media

**Datos de prueba**
Tres centros: uno sin ningún compromiso (cobertura 0%), uno con el compromiso mínimo posible (cobertura ≈1%) y uno con todas sus metas comprometidas (cobertura 100%).

**Pasos detallados**
1. Se preparan los tres centros con las coberturas de prueba (mediante aportes de donante, CU-05).
2. El usuario accede a la vista de mapa.
3. El usuario examina el marcador y la ficha de cada uno de los tres centros.

**Resultados esperados**
El centro con cobertura 0% se muestra como "crítico"; el centro con cobertura 1% se muestra como "en capacidad" (el estado cambia exactamente al pasar de 0); y el centro con cobertura 100% se muestra como "cerrado". Los colores/íconos de los marcadores coinciden con el estado de cada centro.
