from fastapi import APIRouter, Response
from services.files.files_service import FilesService

router = APIRouter(prefix="/files", tags=["files"])
files_service = FilesService()

@router.get("/server-config")
async def get_server_config():
    return await files_service.get_server_config()

@router.get("/server-config-lite")
async def get_server_config_lite():
    return await files_service.get_server_config_lite()

@router.get("/players-data")
async def get_players_data():
    return await files_service.get_ips_banned_whitelist_ops()

@router.get("/mods/download-all")
async def download_all_mods():
    tar_content = await files_service.download_all_mods()
    
    if not tar_content:
        return {"error": "Failed to download mods"}
    
    return Response(
        content=tar_content,
        media_type="application/gzip",
        headers={
            "Content-Disposition": "attachment; filename=mods.tar.gz"
        }
    )