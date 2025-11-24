from fastapi import APIRouter
from pydantic import BaseModel
from services.mods.mods_services import ModsService

router = APIRouter(prefix="/mods", tags=["mods"])
mods_service = ModsService()

class ModInfo(BaseModel):
    id: str
    title: str
    description: str
    icon_url: str
    download_url: str
    project_id: str
    file_name: str

@router.post("/install-ready-mods")
async def install_ready_mods():
    return await mods_service.install_ready_mods()

@router.post("/add-new-mod")
async def add_new_mod(mod: ModInfo):
    return await mods_service.add_new_mod(
        mod.id,
        mod.title,
        mod.description,
        mod.icon_url,
        mod.download_url,
        mod.project_id,
        mod.file_name
    )