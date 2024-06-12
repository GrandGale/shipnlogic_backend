from fastapi import APIRouter, HTTPException, status

from app.common.annotations import DatabaseSession
from app.config.settings import get_settings
from app.super_admin import services
from app.super_admin.schemas import create_schemas, response_schemas

settings = get_settings()

router = APIRouter()


@router.post(
    "",
    summary="Create a new Admin",
    response_description="The created admin's data",
    status_code=status.HTTP_201_CREATED,
    response_model=response_schemas.AdminResponse,
)
async def admin_create(admin_in: create_schemas.AdminCreate, db: DatabaseSession):
    """Create a new admin"""
    created_admin = await services.create_admin(data=admin_in, db=db)

    try:
        await services.create_admin_configuration(admin_id=created_admin.id, db=db)
    except HTTPException as e:
        db.delete(created_admin)
        db.commit()
        raise e

    # Send Notification
    await services.create_admin_notification(
        admin_id=created_admin.id, content="Welcome to ShipNLogic :)", db=db
    )
    return {"data": created_admin}
