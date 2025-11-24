

from fastapi import APIRouter, Query
from services.modrinth.modrinth_service import ModrinthService

router = APIRouter(prefix="/modrinth", tags=["modrinth"])
modrinth_service = ModrinthService()

@router.get("/search/fabric")
async def search_fabric_mods(
    query: str = Query(None, description="Termo de busca"),
    index: str = Query("relevance", description="Índice de ordenação"),
    limit: int = Query(24, description="Número de resultados", ge=1, le=100),
    offset: int = Query(0, description="Deslocamento para paginação", ge=0),
    mc_version: str = Query("1.21.1", description="Versão do Minecraft")
):
    return await modrinth_service.search_default_mods_fabric(query, index, limit, offset, mc_version)

@router.get("/mod/{project_id}")
async def get_version_by_id(project_id: str):
    return await modrinth_service.search_mod_version_game(project_id)

def set_modrinth_authorization(token: str):
    modrinth_service.set_authorization(token)