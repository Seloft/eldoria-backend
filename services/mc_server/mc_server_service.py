import os
import asyncio
from pathlib import Path
from services.docker_s.docker_service import DockerService
from services.mods.mods_services import ModsService


class McServerService:

    def __init__(self):
        self.rcon_password = os.getenv("MINECRAFT_RCON_PASSWORD", "mgmm4103")
        self.docker_service = DockerService()
        self.mods_service = ModsService()
        self.container_name = "eldoria-server"


    async def send_rcon_command(self, command: str) -> str:
        """Envia comando RCON usando rcon-cli via docker exec"""
        from services.files.files_service import FilesService
        fs = FilesService()

        try:
            # Usa rcon-cli dentro do container
            exit_code, output = await self.docker_service.exec_in_container(
                self.container_name,
                f'rcon-cli --password "{self.rcon_password}" "{command}"'
            )

            if exit_code == 0:
                await fs.save_last_command(command)
                list_of_commands = await fs.get_sent_commands()
                return output, list_of_commands
            else:
                print(f"RCON command failed: {output}")
                return "", []

        except Exception as e:
            print(f"Failed to send RCON command: {e}")
            return "", []
        
    async def get_installed_mods(self):
        try:
            return await self.mods_service.get_installed_mods()
        except Exception as e:
            print(f"Error getting installed mods: {e}")
            return []
        
    async def get_ready_to_install_mods(self):
        try:
            return await self.mods_service.get_ready_to_install_mods()
        except Exception as e:
            print(f"Error getting ready to install mods: {e}")
            return []
        
    async def install_ready_mods(self) -> bool:
        try:
            return await self.mods_service.install_ready_mods()
        except Exception as e:
            print(f"Error installing ready mods: {e}")
            return False
        
    async def start_server(self) -> bool:
        try:
            await asyncio.sleep(5)
            return await self.docker_service.start_container("eldoria-server")
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
        
    async def stop_server(self) -> bool:
        try:
            await self.send_rcon_command("say Server is stopping in 15 seconds.")
            await asyncio.sleep(10)
            await self.send_rcon_command("say Server is stopping in 5 seconds.")
            await asyncio.sleep(5)
            await self.send_rcon_command("save-all")
            await asyncio.sleep(2)  # Wait for save to complete
            await self.send_rcon_command("stop")

            return await self.docker_service.stop_container("eldoria-server")
        except Exception as e:
            print(f"Error stopping server: {e}")
            return False
        
    async def restart_server(self) -> bool:
        try:
            await self.send_rcon_command("say Server is restarting in 15 seconds.")
            await asyncio.sleep(10)
            await self.send_rcon_command("say Server is restarting in 5 seconds.")
            await asyncio.sleep(5)
            await self.send_rcon_command("save-all")
            await asyncio.sleep(2)  # Wait for save to complete
            await self.send_rcon_command("stop")

            return await self.docker_service.restart_container("eldoria-server")
        except Exception as e:
            print(f"Error restarting server: {e}")
            return False
        
    async def get_server_status(self) -> str:
        try:
            container = await self.docker_service.get_container("eldoria-server")
            if container:
                return container.status
            return "not_found"
        except Exception as e:
            print(f"Error getting server status: {e}")
            return "error"
        
    async def stream_logs(self, websocket):
        """Stream server logs via WebSocket"""
        try:
            log_file = Path("/minecraft/logs/latest.log")
            
            if not log_file.exists():
                await websocket.send_text("Log file not found yet. Waiting for server to start...\n")
                # Aguarda até o arquivo existir
                for _ in range(30):  # Espera até 30 segundos
                    await asyncio.sleep(1)
                    if log_file.exists():
                        break
            
            if not log_file.exists():
                await websocket.send_text("Server log file not available.\n")
                return
            
            # Lê e envia as últimas 100 linhas primeiro
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                for line in lines[-100:]:
                    await websocket.send_text(line)
            
            # Continua lendo novas linhas em tempo real
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                # Vai para o final do arquivo
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        await websocket.send_text(line)
                    else:
                        # Aguarda por novas linhas
                        await asyncio.sleep(0.1)
                    
        except Exception as e:
            print(f"Error streaming logs: {e}")
            await websocket.close()

    async def get_commands_history(self):
        from services.files.files_service import FilesService
        fs = FilesService()
        try:
            return await fs.get_sent_commands()
        except Exception as e:
            print(f"Error getting commands history: {e}")
            return []
        
    async def remove_mod(self, mod_id: str) -> bool:
        from services.files.files_service import FilesService
        try:
            return await FilesService().remove_installed_mod(id=mod_id)
        except Exception as e:
            print(f"Error removing mod {mod_id}: {e}")
            return False
        
    async def remove_ready_mod(self, mod_id: str) -> bool:
        from services.files.files_service import FilesService
        try:
            return await FilesService().remove_ready_to_install_mod(id=mod_id)
        except Exception as e:
            print(f"Error removing ready mod {mod_id}: {e}")
            return False