from pathlib import Path
import shutil
import asyncio
from services.docker_s.docker_service import DockerService
from services.files.files_service import FilesService

class ModsService:

    def __init__(self):
        self.docker_service = DockerService()
        self.files_service = FilesService()
        self.mods_path = "/minecraft/mods/"
        self.mods_backup_path = "/minecraft/mods_backup/"
            
    async def install_ready_mods(self) -> bool:
        try:
            
            mods_already_installed = await self.files_service.get_installed_mods()
            mods_to_install = await self.files_service.get_ready_to_install_mods()

            if not mods_to_install:
                print("No mods to install.")
                return False

            if mods_already_installed and len(mods_already_installed) > 0:
                if not await self.temp_mods_backup():
                    print("Failed to backup mods. Aborting installation.")
                    return False

            if not await self.clear_mods_folder():
                print("Failed to clear mods folder. Aborting installation.")
                return False

            for mod in mods_to_install:
                if mods_already_installed and mod["id"] in [installed_mod["id"] for installed_mod in mods_already_installed]:
                    print(f"Mod {mod['title']} already installed, skipping.")
                    continue

                if await self.files_service.add_installed_mod(mod_info=mod, path=self.mods_path):
                    print(f"Mod {mod['title']} installed successfully.")
                else:
                    print(f"Failed to install mod {mod['title']}.")

            if not await self.files_service.clear_list_after_install():
                print("Failed to clear ready to install mods list.")
                return False

            return True
        
        except Exception as e:
            print(f"Error installing mods: {e}")
            return False

    async def temp_mods_backup(self) -> bool:
        try:
            timestamp = await self.docker_service.get_current_timestamp()
            mods_dir = Path(self.mods_path.rstrip('/'))
            backup_dir = Path(self.mods_backup_path.rstrip('/')) / f"backup_{timestamp}"

            # Cria o diretório de backup se não existir
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copia os mods para o backup usando shutil
            if mods_dir.exists():
                for mod_file in mods_dir.glob('*.jar'):
                    shutil.copy2(mod_file, backup_dir / mod_file.name)
            
            print(f"Mods backup created successfully at {backup_dir}")
            return True
        
        except Exception as e:
            print(f"Error creating temporary mods backup: {e}")
            return False
        
    # Create restore_mods_backup method if needed

    async def add_new_mod(self, id: str, title: str, description: str, icon_url: str, download_url: str, project_id: str, file_name: str):
        try:
            mod_info = {
                "id": id,
                "title": title,
                "description": description,
                "icon_url": icon_url,
                "download_url": download_url,
                "project_id": project_id,
                "file_name": file_name
            }

            response = await self.files_service.add_ready_to_install_mod(mod_info=mod_info)
            return response
        
        except Exception as e:
            print(f"Error adding new mod: {e}")
            return False
        
    async def get_installed_mods(self):
        try:
            installed_mods = await self.files_service.get_installed_mods()
            return installed_mods
        
        except Exception as e:
            print(f"Error retrieving installed mods: {e}")
            return []
        
    async def get_ready_to_install_mods(self):
        try:
            ready_mods = await self.files_service.get_ready_to_install_mods()
            return ready_mods
        
        except Exception as e:
            print(f"Error retrieving ready to install mods: {e}")
            return []
        
    async def clear_mods_folder(self) -> bool:
        try:
            # Remove todos os arquivos .jar da pasta mods
            mods_dir = Path(self.mods_path.rstrip('/'))
            
            if not mods_dir.exists():
                print(f"Mods folder does not exist: {mods_dir}")
                return False
            
            jar_files = list(mods_dir.glob('*.jar'))
            for jar_file in jar_files:
                jar_file.unlink()
            
            print(f"Mods folder cleared successfully: {len(jar_files)} files removed")
            return True
        
        except Exception as e:
            print(f"Error clearing mods folder: {e}")
            return False