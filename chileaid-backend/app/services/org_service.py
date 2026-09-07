"""Lógica de negocio del panel de la Organización Receptora.

Resuelve el centro de una organización y construye sus DTO calculando la
`cobertura` (derivada, nunca persistida) y los totales agregados. El router
decide los códigos de "ubicación" (404 sin centro/insumo/necesidad); las
**reglas de negocio** del alta/edición (no duplicar insumo activo, no editar una
necesidad cerrada, no bajar la meta por debajo de lo comprometido) viven y se
hacen valer aquí, lanzando `HTTPException` (409/422).
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import create_access_token, hash_password
from app.models import (
    ActivityType,
    Center,
    CenterStatus,
    Donation,
    DonationItem,
    DonationStatus,
    Emergency,
    EmergencyStatus,
    Insumo,
    MotivoCancelacion,
    Need,
    NeedStatus,
    Organization,
    OrganizationStatus,
    Urgencia,
    User,
    UserRole,
)
from app.schemas.auth import OrgRegisterRequest, RegisterDonorRequest
from app.schemas.org import (
    CenterCreateDTO,
    CenterTotalesDTO,
    CenterUpdateDTO,
    EmergenciaRefDTO,
    InsumoCatalogDTO,
    InsumoDTO,
    NeedCreateDTO,
    NeedDTO,
    NeedUpdateDTO,
    OrgCenterDTO,
    OrgProfileDTO,
    UpdateOrgProfileDTO,
)
from app.services import geocoding_service
from app.services.activity_service import record_activity


def _cobertura(comprometida: int, requerida: int) -> int:
    """Porcentaje 0-100 cubierto. Maneja división por cero (sin meta → 0%)."""
    if requerida <= 0:
        return 0
    return round(comprometida / requerida * 100)


def _center_estado(center: Center, cobertura_general: int) -> str:
    """Deriva la SATURACIÓN visual del centro a partir de la cobertura.

    Contrato del frontend: 0% → `critico`, 1-99% → `en_capacidad`,
    100% → `cerrado`. El cierre manual (CenterStatus.CERRADO) también es
    `cerrado`.
    """
    if center.estado == CenterStatus.CERRADO:
        return "cerrado"
    if cobertura_general >= 100:
        return "cerrado"
    if cobertura_general == 0:
        return "critico"
    return "en_capacidad"


def get_center_by_organization(
    db: Session, organization_id: uuid.UUID
) -> Center | None:
    """Centro de la organización con sus needs e insumos precargados (sin N+1).

    Devuelve None si la organización aún no tiene un centro asociado; el router
    decide qué hacer con eso.
    """
    return db.scalar(
        select(Center)
        .where(Center.organization_id == organization_id)
        .order_by(Center.created_at)
        .options(selectinload(Center.needs).joinedload(Need.insumo))
    )


def build_need_dto(need: Need) -> NeedDTO:
    """Construye el NeedDTO de una necesidad, con su cobertura derivada."""
    return NeedDTO(
        id=str(need.id),
        insumo=InsumoDTO(
            nombre=need.insumo.nombre,
            categoria=need.insumo.categoria.value,
            unidad=need.insumo.unidad,
        ),
        cantidad_requerida=need.cantidad_requerida,
        cantidad_comprometida=need.cantidad_comprometida,
        cantidad_recibida=need.cantidad_recibida,
        urgencia=need.urgencia.value,
        estado=need.estado.value,
        cobertura=_cobertura(need.cantidad_comprometida, need.cantidad_requerida),
    )


def build_org_center_dto(center: Center) -> OrgCenterDTO:
    """Construye el OrgCenterDTO: necesidades + totales agregados + estado."""
    necesidades = [build_need_dto(n) for n in center.needs]

    total_requerida = sum(n.cantidad_requerida for n in necesidades)
    total_comprometida = sum(n.cantidad_comprometida for n in necesidades)
    total_recibida = sum(n.cantidad_recibida for n in necesidades)
    cobertura_general = _cobertura(total_comprometida, total_requerida)

    emergencia = (
        EmergenciaRefDTO(
            id=str(center.emergency.id),
            nombre=center.emergency.nombre,
            estado=center.emergency.estado.value,
        )
        if center.emergency is not None
        else None
    )

    return OrgCenterDTO(
        id=str(center.id),
        nombre=center.nombre,
        direccion=center.direccion,
        zona=center.zona,
        horario_atencion=center.horario_atencion,
        estado=_center_estado(center, cobertura_general),
        latitud=float(center.latitud) if center.latitud is not None else None,
        longitud=float(center.longitud) if center.longitud is not None else None,
        emergencia=emergencia,
        necesidades=necesidades,
        totales=CenterTotalesDTO(
            cantidad_requerida=total_requerida,
            cantidad_comprometida=total_comprometida,
            cantidad_recibida=total_recibida,
            cobertura_general=cobertura_general,
        ),
    )


def _resolve_linkable_emergency(
    db: Session, emergency_id: uuid.UUID
) -> Emergency:
    """Valida que la org pueda vincular su centro a esta emergencia.

    404 si no existe; 422 si está `cerrada` (una org solo se vincula a una
    emergencia ACTIVA). Solo se llama cuando el `emergencyId` cambia respecto al
    valor actual del centro, así que un vínculo histórico a una cerrada no se
    revalida al editar otros campos.
    """
    emergency = db.get(Emergency, emergency_id)
    if emergency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La emergencia seleccionada no existe",
        )
    if emergency.estado != EmergencyStatus.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No puedes vincular tu centro a una emergencia cerrada",
        )
    return emergency


def _resolve_center_coords(
    data: CenterCreateDTO | CenterUpdateDTO,
) -> tuple[float | None, float | None]:
    """Coordenadas a persistir para un centro (RF-05).

    Precedencia: si el usuario mandó **ambas** coordenadas (p. ej. eligió el punto
    exacto en el mapa), se usan tal cual. Si no vinieron, se **geocodifica** la
    dirección como fallback (Nominatim); si el geocode falla, quedan `null` (el
    alta no se bloquea — la org puede fijar el punto después desde el mapa).
    """
    if data.latitud is not None and data.longitud is not None:
        return data.latitud, data.longitud

    hit = geocoding_service.geocode(f"{data.direccion}, {data.zona}, Chile")
    if hit is None:
        return None, None
    return hit.latitud, hit.longitud


def create_center_for_organization(
    db: Session, organization_id: uuid.UUID, data: CenterCreateDTO
) -> OrgCenterDTO:
    """Crea el centro de la organización autenticada (CU-08), uno por org.

    Regla de negocio: una organización tiene como máximo un centro. No hay
    `unique(organization_id)` en la BD, así que la unicidad se impone aquí →
    409 si ya existe. El centro nace operativo (`estado=ACTIVO`). Puede nacer
    vinculado a una emergencia ACTIVA si viene `emergencyId` (404/422 si no es
    válida), o sin emergencia si viene `null`. Sin necesidades, sus totales dan 0
    y el `estado` derivado (saturación) es `critico`.
    """
    existing = get_center_by_organization(db, organization_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La organización ya tiene un centro registrado",
        )

    emergency_id = None
    if data.emergency_id is not None:
        emergency_id = _resolve_linkable_emergency(db, data.emergency_id).id

    latitud, longitud = _resolve_center_coords(data)
    center = Center(
        organization_id=organization_id,
        emergency_id=emergency_id,
        nombre=data.nombre,
        zona=data.zona,
        direccion=data.direccion,
        horario_atencion=data.horario_atencion,
        latitud=latitud,
        longitud=longitud,
        estado=CenterStatus.ACTIVO,
    )
    db.add(center)
    db.commit()
    db.refresh(center)
    return build_org_center_dto(center)


def update_center_for_organization(
    db: Session, organization_id: uuid.UUID, data: CenterUpdateDTO
) -> OrgCenterDTO:
    """Edita el centro de la organización autenticada (CU-08).

    404 si la org aún no tiene centro (debería usar POST). Actualiza los campos
    editables **incluido `emergencyId`** (vincular/cambiar/desvincular); NO toca
    `estado` (operatividad) ni las necesidades. El vínculo con la emergencia solo
    se re-valida (ACTIVA, 404/422) cuando cambia respecto al valor actual, así que
    editar otros campos de un centro atado a una emergencia ya cerrada (histórico)
    no falla. La saturación y los totales del DTO se siguen derivando.
    """
    center = get_center_by_organization(db, organization_id)
    if center is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización aún no tiene un centro registrado",
        )

    center.nombre = data.nombre
    center.direccion = data.direccion
    center.zona = data.zona
    center.horario_atencion = data.horario_atencion
    center.latitud, center.longitud = _resolve_center_coords(data)
    # Solo re-valida si el vínculo cambia: preserva el histórico a una cerrada.
    if data.emergency_id != center.emergency_id:
        if data.emergency_id is None:
            center.emergency_id = None
        else:
            center.emergency_id = _resolve_linkable_emergency(
                db, data.emergency_id
            ).id
    db.commit()
    db.refresh(center)
    return build_org_center_dto(center)


def list_insumos_catalog(db: Session) -> list[InsumoCatalogDTO]:
    """Catálogo de insumos solicitables ACTIVOS, ordenado por nombre.

    Expone el `id` real (UUID) de cada insumo, que el alta de una necesidad
    necesita como `insumoId`. Los dados de baja por el admin (`activo=False`,
    soft-delete) NO se listan ni para las orgs ni para el panel admin.
    """
    insumos = db.scalars(
        select(Insumo).where(Insumo.activo == True).order_by(Insumo.nombre)  # noqa: E712
    ).all()
    return [
        InsumoCatalogDTO(
            id=str(i.id),
            nombre=i.nombre,
            categoria=i.categoria.value,
            unidad=i.unidad,
            activo=i.activo,
        )
        for i in insumos
    ]


def get_insumo(db: Session, insumo_id: uuid.UUID) -> Insumo | None:
    """Insumo del catálogo por id, o None si no existe."""
    return db.get(Insumo, insumo_id)


def get_need_in_center(
    db: Session, need_id: uuid.UUID, center: Center
) -> Need | None:
    """Necesidad por id, SOLO si pertenece al centro dado (aísla por org).

    Devuelve None tanto si no existe como si es de otro centro: el router lo
    traduce a 404 sin revelar la existencia ajena.
    """
    return db.scalar(
        select(Need)
        .where(Need.id == need_id, Need.center_id == center.id)
        .options(joinedload(Need.insumo))
    )


def create_need(
    db: Session, center: Center, insumo: Insumo, data: NeedCreateDTO
) -> NeedDTO:
    """Crea una necesidad para el centro. Nace sin compromisos ni recepciones.

    Regla de negocio: no se permite más de una necesidad ACTIVA por insumo en el
    mismo centro (se edita la existente en vez de duplicar) → 409 Conflict. Las
    cerradas/completadas no bloquean (se puede volver a solicitar el insumo).
    """
    existing_activa = db.scalar(
        select(Need).where(
            Need.center_id == center.id,
            Need.insumo_id == insumo.id,
            Need.estado == NeedStatus.ACTIVA,
        )
    )
    if existing_activa is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe una necesidad activa para este insumo; edítala en "
                "lugar de crear una nueva"
            ),
        )

    need = Need(
        center_id=center.id,
        insumo_id=insumo.id,
        cantidad_requerida=data.cantidad_requerida,
        cantidad_comprometida=0,
        cantidad_recibida=0,
        urgencia=Urgencia(data.urgencia),
        estado=NeedStatus.ACTIVA,
    )
    # Adjuntamos el insumo ya cargado para que build_need_dto no dispare otra query.
    need.insumo = insumo
    db.add(need)
    db.commit()
    db.refresh(need)
    return build_need_dto(need)


def update_need(db: Session, need: Need, data: NeedUpdateDTO) -> NeedDTO:
    """Actualiza cantidad requerida y urgencia de una necesidad (el insumo no cambia).

    Reglas de negocio (en orden de precedencia):
    - Una necesidad COMPLETADA o CERRADA no se puede editar → 409 Conflict.
    - La nueva meta no puede quedar por debajo de lo ya comprometido → 422
      (rompería el invariante de no-sobrestock, `ck_need_no_sobrestock`).
    """
    if need.estado in (NeedStatus.COMPLETADA, NeedStatus.CERRADA):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede editar una necesidad completada o cerrada",
        )
    if data.cantidad_requerida < need.cantidad_comprometida:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "La cantidad requerida no puede ser menor a lo ya comprometido "
                f"({need.cantidad_comprometida})"
            ),
        )

    need.cantidad_requerida = data.cantidad_requerida
    need.urgencia = Urgencia(data.urgencia)
    db.commit()
    db.refresh(need)
    return build_need_dto(need)


def close_need(db: Session, need: Need) -> NeedDTO:
    """Cierre manual de una necesidad por la organización (CU-03): estado → CERRADA.

    Solo una necesidad ACTIVA se puede cerrar; una ya completada/cerrada da 409
    (mismo estilo que el 409 de `update_need`).

    Cascada de cancelación: los aportes PENDIENTE contra esta necesidad ya no se
    recibirán, así que se cancelan (soft) sus ítems activos (`motivo=CIERRE_NECESIDAD`)
    y se revierte lo comprometido. Cada donación afectada pasa a CANCELADA solo si
    NO le queda ningún ítem activo (puede cubrir otras needs del centro). Lo ya
    `RECIBIDO` (`cantidad_recibida`) no se toca.
    """
    if need.estado != NeedStatus.ACTIVA:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede cerrar una necesidad completada o cerrada",
        )

    # Relee la need con FOR UPDATE para serializar con create_donation/confirm/cancel
    # (todos lockean la Need): así lo comprometido no cambia bajo nuestros pies.
    need = db.scalar(select(Need).where(Need.id == need.id).with_for_update())
    need.estado = NeedStatus.CERRADA

    # Ítems activos de donaciones PENDIENTE que referencian esta need.
    items = (
        db.scalars(
            select(DonationItem)
            .join(DonationItem.donation)
            .where(
                DonationItem.need_id == need.id,
                DonationItem.activo.is_(True),
                Donation.estado == DonationStatus.PENDIENTE,
            )
            .options(selectinload(DonationItem.donation).selectinload(Donation.items))
        )
        .unique()
        .all()
    )
    for item in items:
        item.activo = False
        item.motivo_cancelacion = MotivoCancelacion.CIERRE_NECESIDAD
        need.cantidad_comprometida -= item.cantidad
        # La donación padre se cancela solo si ya no le queda ningún ítem activo.
        if all(not it.activo for it in item.donation.items):
            item.donation.estado = DonationStatus.CANCELADA

    db.commit()
    db.refresh(need)
    return build_need_dto(need)


# ----------------------------------------------------------------------------
# Perfil de la organización (CU-09)
# ----------------------------------------------------------------------------


def get_organization(
    db: Session, organization_id: uuid.UUID
) -> Organization | None:
    """Organización del token con su User-representante y documentos precargados.

    `joinedload` evita N+1 al construir el perfil (necesita `user.email` y el
    primer documento). Devuelve None si el id no resuelve (el router → 404).
    """
    return db.scalar(
        select(Organization)
        .where(Organization.id == organization_id)
        .options(
            joinedload(Organization.user),
            selectinload(Organization.documents),
        )
    )


def build_org_profile_dto(org: Organization) -> OrgProfileDTO:
    """Construye el OrgProfileDTO a partir del modelo real.

    `tipo` = `tipo_centro`; `email` = del User-representante (no de la org);
    `documentacion` = nombre del primer documento (o "" si no hay);
    `fechaRegistro` = `created_at` truncado a fecha ISO.
    """
    documentacion = org.documents[0].nombre_archivo if org.documents else ""
    return OrgProfileDTO(
        id=str(org.id),
        nombre=org.nombre,
        tipo=org.tipo_centro.value,
        rut=org.rut or "",  # rut es opcional en el alta (CU-01); "" si no se informó
        contacto_nombre=org.contacto_nombre,
        email=org.user.email,
        telefono=org.telefono,
        documentacion=documentacion,
        estado=org.estado.value,
        fecha_registro=org.created_at.date().isoformat(),
        region=org.region,
        motivo_rechazo=org.motivo_rechazo,
    )


def update_org_profile(
    db: Session, organization_id: uuid.UUID, payload: UpdateOrgProfileDTO
) -> OrgProfileDTO:
    """Actualiza los datos de contacto de la organización autenticada (CU-09).

    `contacto_nombre`/`telefono`/`region` van directo a `organizations`. El
    `email` vive en el User-representante: si cambia, se verifica que no esté
    tomado por OTRA cuenta (409) antes de actualizar `users.email`.
    """
    org = get_organization(db, organization_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La organización no existe",
        )

    org.contacto_nombre = payload.contacto_nombre
    org.telefono = payload.telefono
    org.region = payload.region

    if payload.email != org.user.email:
        taken = db.scalar(
            select(User).where(
                User.email == payload.email, User.id != org.user_id
            )
        )
        if taken is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está en uso por otra cuenta",
            )
        org.user.email = payload.email

    db.commit()
    db.refresh(org)
    return build_org_profile_dto(org)


# ----------------------------------------------------------------------------
# Registro de la organización (CU-01)
# ----------------------------------------------------------------------------


def register_organization(db: Session, data: OrgRegisterRequest) -> str:
    """Alta de una organización receptora y su cuenta-representante (CU-01).

    Crea, en una sola transacción, el `User` (role=ORG, password hasheada) y la
    `Organization` (estado PENDIENTE). 409 si el email ya está registrado en
    `users`. Emite un JWT igual al de `/auth/login` (mismos claims: `sub`,
    `role`, `organization_id`) para que el frontend pueda subir el documento de
    respaldo inmediatamente después del alta sin pedir credenciales de nuevo;
    la org sigue Pendiente hasta la aprobación del admin (CU-02) — el token no
    cambia ese estado, solo autoriza las llamadas a `/org/documents/*` durante
    el propio registro. Si el commit falla (p. ej. RUT duplicado), se revierte
    todo para no dejar un User huérfano.
    """
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.ORG,
    )
    db.add(user)
    db.flush()  # asigna user.id sin cerrar la transacción

    org = Organization(
        user_id=user.id,
        nombre=data.nombre,
        rut=data.rut,
        tipo_centro=data.tipo_centro,
        direccion=data.direccion,
        region=data.region,
        contacto_nombre=data.contacto_nombre,
        telefono=data.telefono,
        estado=OrganizationStatus.PENDIENTE,
    )
    db.add(org)
    db.flush()  # asigna org.id para el evento de actividad
    record_activity(
        db,
        ActivityType.ORG_REGISTRADA,
        f"{data.nombre} solicitó registro",
        organization_id=org.id,
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return create_access_token(
        {"sub": str(user.id), "role": user.role.value, "organization_id": str(org.id)}
    )


def register_donor(db: Session, data: RegisterDonorRequest) -> str:
    """Crea la cuenta de un donante particular e inicia sesión inmediatamente.

    A diferencia del registro de org, el donante no requiere aprobación: se
    emite el JWT en el acto. 409 si el email ya existe en `users` (sin filtrar
    por rol — un email es único en toda la plataforma).
    """
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.DONOR,
        nombre=data.nombre,
        apellido=data.apellido,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token({"sub": str(user.id), "role": user.role.value})
