from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from services.mc_server.mc_server_service import McServerService

router = APIRouter(prefix="/mc-server", tags=["mc_server"])
mc_server_service = McServerService()

class CommandPayload(BaseModel):
    command: str

@router.get("/mods")
async def get_installed_mods():
    return  await mc_server_service.get_installed_mods()

@router.get("/mods/ready")
async def get_ready_to_install_mods():
    return await mc_server_service.get_ready_to_install_mods()

@router.post("/mods/install")
async def install_ready_mods():
    success = await mc_server_service.install_ready_mods()
    return {"success": success}

@router.post("/mods/remove/{mod_id}")
async def remove_mod(mod_id: str):
    success = await mc_server_service.remove_mod(mod_id)
    return {"success": success}

@router.post("/mods/ready/remove/{mod_id}")
async def remove_ready_mod(mod_id: str):
    success = await mc_server_service.remove_ready_mod(mod_id)
    return {"success": success}

@router.post("/start")
async def start_server():
    success = await mc_server_service.start_server()
    return {"success": success}

@router.post("/stop")
async def stop_server():
    success = await mc_server_service.stop_server()
    return {"success": success}

@router.post("/restart")
async def restart_server():
    success = await mc_server_service.restart_server()
    return {"success": success}

@router.get("/status")
async def get_server_status():
    return await mc_server_service.get_server_status()

@router.post("/command")
async def send_server_command(payload: CommandPayload):
    response, list_of_commands = await mc_server_service.send_rcon_command(payload.command)
    return {"response": response, "commands_history": list_of_commands}

@router.get("/commands-history")
async def get_commands_history():
    list_of_commands = await mc_server_service.get_commands_history()
    return {"commands_history": list_of_commands}

@router.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    try:
        await mc_server_service.stream_logs(websocket)
    except WebSocketDisconnect:
        print("Client disconnected from logs stream")