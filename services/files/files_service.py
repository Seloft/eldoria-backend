import json
import aiofiles
import aiohttp
import tarfile
from pathlib import Path
import shutil
from services.docker_s.docker_service import DockerService

class FilesService:
    
    def __init__(self):
        self.docker_service = DockerService()
        self.minecraft_server_path = "/minecraft/"
        
        self.minecraft_ready_mods = "config/ready_to_install.json"
        self.minecraft_installed_mods = "config/installed_mods.json"
        self.minecraft_sent_commands = "config/sent_commands.json"

    async def get_server_config(self):
        
        try:

            container = await self.docker_service.get_container("minecraft-server")

            if not container:
                return None
        
            config_path = f"{self.minecraft_server_path}server.properties"
            exit_code, output = await self.docker_service.exec_in_container("minecraft-server", f"cat {config_path}")

            if exit_code == 0:
                config_content = output
                config_lines = config_content.splitlines()
                config_dict = {}
                
                for line in config_lines:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config_dict[key.strip()] = value.strip()
                
                return config_dict
        
        except Exception as e:
            print(f"Error retrieving server config: {e}")
            return None
        
    async def get_server_config_lite(self):
        
        try:
            container = await self.docker_service.get_container("minecraft-server")

            if not container:
                return None
            
            config_path = f"{self.minecraft_server_path}server.properties"
            exit_code, output = await self.docker_service.exec_in_container("minecraft-server", f"cat {config_path}")

            if exit_code == 0:
                config_content = output
                config_lines = config_content.splitlines()
                config_dict = {}
                
                for line in config_lines:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config_dict[key.strip()] = value.strip()
                
                lite_config = {
                    "difficulty": config_dict.get("difficulty"),
                    "gamemode": config_dict.get("gamemode"),
                    "hardcore": config_dict.get("hardcore"),
                    "simulation-distance": config_dict.get("simulation-distance"),
                    "server-port": config_dict.get("server-port"),
                    "pvp": config_dict.get("pvp"),
                    "rcon.password": config_dict.get("rcon.password"),
                    "rcon.port": config_dict.get("rcon.port"),
                    "enable-rcon": config_dict.get("enable-rcon"),
                    "level-seed": config_dict.get("level-seed"),
                    "max-world-size": config_dict.get("max-world-size"),
                    "max-tick-time": config_dict.get("max-tick-time"),
                    "max-players": config_dict.get("max-players"),
                    "motd": config_dict.get("motd"),
                    "white-list": config_dict.get("white-list"),
                    "view-distance": config_dict.get("view-distance"),
                }
                
                return lite_config
        
        except Exception as e:
            print(f"Error retrieving lite server config: {e}")
            return None
        
    async def get_ips_banned_whitelist_ops(self):
        try:
            container = await self.docker_service.get_container("minecraft-server")
            if not container:
                return None
            
            files = {
                "banned-ips": f"{self.minecraft_server_path}banned-ips.json",
                "banned-players": f"{self.minecraft_server_path}banned-players.json",
                "whitelist": f"{self.minecraft_server_path}whitelist.json",
                "ops": f"{self.minecraft_server_path}ops.json"
            }
            
            data = {}
            
            for key, path in files.items():
                exit_code, output = await self.docker_service.exec_in_container("minecraft-server", f"cat {path}")
                
                if exit_code == 0:
                    try:
                        json_data = json.loads(output)
                        
                        if key == "banned-ips":
                            data[key] = [item["ip"] for item in json_data]
                        elif key == "banned-players":
                            data[key] = [item["name"] for item in json_data]
                        elif key == "whitelist":
                            data[key] = [item["name"] for item in json_data]
                        elif key == "ops":
                            data[key] = [item["name"] for item in json_data]
                    except json.JSONDecodeError:
                        data[key] = []
                else:
                    data[key] = []
            
            return data
        
        except Exception as e:
            print(f"Error retrieving banned IPs, whitelist, Banned Players and ops: {e}")
            return None
        
    async def get_installed_mods(self) -> list:
        try:
            
            if not self.minecraft_installed_mods:
                return None
            
            async with aiofiles.open(self.minecraft_installed_mods, 'r') as f:
                content = await f.read()
                installed_mods = json.loads(content)
                return installed_mods
            
        except Exception as e:
            print(f"Error retrieving installed mods: {e}")
            return None
        
    async def clear_list_after_install(self) -> bool:
        try:
            async with aiofiles.open(self.minecraft_ready_mods, 'w') as f:
                await f.write(json.dumps([], indent=4))
            return True
        except Exception as e:
            print(f"Error clearing ready to install mods list: {e}")
            return False

    async def get_ready_to_install_mods(self) -> list:
        try:
            
            if not self.minecraft_ready_mods:
                return None
            
            async with aiofiles.open(self.minecraft_ready_mods, 'r') as f:
                content = await f.read()
                ready_mods = json.loads(content)
                return ready_mods
            
        except Exception as e:
            print(f"Error retrieving ready to install mods: {e}")
            return None
        
    async def add_installed_mod(self, mod_info: dict, path: str):
        try:
            
            installed_mods = await self.get_installed_mods()
            if installed_mods is None:
                installed_mods = []

            print(f"Downloading mod {mod_info['title']} from {mod_info['download_url']}...")
            
            # Download usando aiohttp diretamente para o volume montado
            mods_dir = Path(path.rstrip('/'))
            mods_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = mods_dir / mod_info['file_name']
            
            async with aiohttp.ClientSession() as session:
                async with session.get(mod_info['download_url']) as response:
                    if response.status == 200:
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(await response.read())
                    else:
                        print(f"Failed to download mod: HTTP {response.status}")
                        return False
            
            mod_info['installed_at'] = await self.docker_service.get_current_timestamp()
            installed_mods.append(mod_info)
            
            async with aiofiles.open(self.minecraft_installed_mods, 'w') as f:
                await f.write(json.dumps(installed_mods, indent=4))
            
            return True
            
        except Exception as e:
            print(f"Error adding installed mod: {e}")
            return False
        
    async def remove_installed_mod(self, id: str) -> bool:
        try:
            installed_mods = await self.get_installed_mods()
            if installed_mods is None:
                return False

            mod_to_remove = next((mod for mod in installed_mods if mod["id"] == id), None)
            if not mod_to_remove:
                print(f"Mod with ID {id} not found in installed mods.")
                return False

            dependencies = [mod for mod in installed_mods if id in mod.get("dependency_of", [])]
            if not dependencies:
                dependencies = []
            
            dependencies_to_remove = []
            for dep in dependencies:
                
                if len(dep.get("dependency_of", [])) > 1:
                    print(f"Mod {dep['title']} is a dependency for other mods as well. Skipping removal.")
                    dep["dependency_of"].remove(id)
                    continue

                dependencies_to_remove.append(dep)

            mods_to_remove = [mod_to_remove] + dependencies_to_remove
            for mod in mods_to_remove:
                mod_file = Path(f"{self.minecraft_server_path}mods/{mod['file_name']}")
                
                if mod_file.exists():
                    mod_file.unlink()
                    print(f"Removed mod file: {mod['file_name']}")
                else:
                    print(f"Mod file not found: {mod['file_name']}")

                installed_mods.remove(mod)
            
            async with aiofiles.open(self.minecraft_installed_mods, 'w') as f:            
                await f.write(json.dumps(installed_mods, indent=4))

            self.docker_service.restart_container("minecraft-server")
            return True
        
        except Exception as e:
            print(f"Error removing installed mod: {e}")
            return False

    async def add_ready_to_install_mod(self, mod_info: dict, recursive: bool = True):
        try:
            from services.modrinth.modrinth_service import ModrinthService

            all_mods = await self.get_installed_mods() + await self.get_ready_to_install_mods()
            
            for mod in all_mods:
                if mod["project_id"] == mod_info["project_id"]:
                    return "One version of this mod is already added"

            ready_mods = await self.get_ready_to_install_mods()
            if ready_mods is None:
                ready_mods = []
            
            if recursive: 
                dependencies = await ModrinthService().recursive_dependencies(mod_info["id"])

                for mod_dep in dependencies["mods"]:
                    if not any(mod["project_id"] == mod_dep["project_id"] for mod in all_mods):
                        ready_mods.append(mod_dep)
                    else:
                        existing = next((m for m in ready_mods if m["project_id"] == mod_dep["project_id"]), None)
                        if existing:
                            if "dependency_of" not in existing:
                                existing["dependency_of"] = []
                            if mod_info["id"] not in existing["dependency_of"]:
                                existing["dependency_of"].append(mod_info["id"])

                ready_mods.append(mod_info)
            else:
                ready_mods.append(mod_info)
            
            async with aiofiles.open(self.minecraft_ready_mods, 'w') as f:
                await f.write(json.dumps(ready_mods, indent=4))
            
            return "Mod added to ready to install list"
            
        except Exception as e:
            print(f"Error adding ready to install mod: {e}")
            return "Failed to add mod"
        
    async def remove_ready_to_install_mod(self, id: str) -> bool:
        try:
            ready_mods = await self.get_ready_to_install_mods()
            if ready_mods is None:
                return False

            mod_to_remove = next((mod for mod in ready_mods if mod["id"] == id), None)
            if not mod_to_remove:
                print(f"Mod with ID {id} not found in ready to install mods.")
                return False

            dependencies = [mod for mod in ready_mods if id in mod.get("dependency_of", [])]
            if not dependencies:
                dependencies = []
            
            dependencies_to_remove = []
            for dep in dependencies:
                
                if len(dep.get("dependency_of", [])) > 1:
                    print(f"Mod {dep['title']} is a dependency for other mods as well. Skipping removal.")
                    dep["dependency_of"].remove(id)
                    continue

                dependencies_to_remove.append(dep)

            mods_to_remove = [mod_to_remove] + dependencies_to_remove
            for mod in mods_to_remove:
                ready_mods.remove(mod)
            
            async with aiofiles.open(self.minecraft_ready_mods, 'w') as f:            
                await f.write(json.dumps(ready_mods, indent=4))

            return True
        
        except Exception as e:
            print(f"Error removing ready to install mod: {e}")
            return False
        
    async def get_files_by_project_id(self, project_id: str) -> tuple:
        try:

            version = None
            installed = False
            ready = False

            installed_mods = await self.get_installed_mods()
            ready_mods = await self.get_ready_to_install_mods()

            for mod in installed_mods:
                if mod.get("project_id") == project_id:
                    version = mod.get("id")
                    installed = True
                    break
            
            if not installed:
                for mod in ready_mods:
                    if mod.get("project_id") == project_id:
                        version = mod.get("id")
                        ready = True
                        break

            return version, installed, ready
        
        except Exception as e:
            print(f"Error getting files by project ID: {e}")
            return None

    async def save_last_command(self, command_info: str) -> bool:
        try:
            commands = []
            timestamp = await self.docker_service.get_current_timestamp()
            command_info = {"timestamp": timestamp, "command": command_info}

            try:
                async with aiofiles.open(self.minecraft_sent_commands, 'r') as f:
                    content = await f.read()
                    commands = json.loads(content)
            except FileNotFoundError:
                commands = []
            
            commands.append(command_info)
            
            async with aiofiles.open(self.minecraft_sent_commands, 'w') as f:
                await f.write(json.dumps(commands, indent=4))
            
            return True
            
        except Exception as e:
            print(f"Error saving last command: {e}")
            return False
        
    async def get_sent_commands(self):
        try:
            async with aiofiles.open(self.minecraft_sent_commands, 'r') as f:
                content = await f.read()
                commands = json.loads(content)
                return commands
        except Exception as e:
            print(f"Error retrieving sent commands: {e}")
            return []
        
    async def download_all_mods(self):
        try:
            mods_path = Path(f"{self.minecraft_server_path}mods")
            tar_path = Path(f"{self.minecraft_server_path}mods.tar.gz")

            if not mods_path.exists():
                print(f"Mods folder not found: {mods_path}")
                return None

            # Cria arquivo tar.gz com os mods usando tarfile
            with tarfile.open(tar_path, "w:gz") as tar:
                for mod_file in mods_path.glob('*.jar'):
                    tar.add(mod_file, arcname=mod_file.name)

            # Lê o conteúdo do arquivo compactado
            async with aiofiles.open(tar_path, 'rb') as f:
                tar_content = await f.read()

            # Limpa o arquivo temporário
            tar_path.unlink()

            return tar_content  # Retorna bytes do arquivo tar.gz

        except Exception as e:
            print(f"Error downloading all mods: {e}")
            return None