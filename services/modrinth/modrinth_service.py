import httpx
import services.files.files_service as files_service

class ModrinthService:

    def __init__(self):
        self.base_url = "https://api.modrinth.com/v2"
        self.Authorization = None


    def set_authorization(self, token: str):
        self.Authorization = token

    async def search_default_mods_fabric(self, query: str = None, index: str = "relevance", limit: int = 24, offset: int = 0, mc_version: str = "1.21.1"):
        """Search for Fabric mods compatible with Minecraft 1.21.1, including only server-side optional or required mods."""
        headers = {}
        if self.Authorization:
            headers["Authorization"] = self.Authorization

        url = f"{self.base_url}/search"

        params = {
            "query": query,
            "index": index,
            "limit": limit,
            "offset": offset,
            "facets": f'[["categories:fabric"],["versions:{mc_version}"],["project_type:mod"],["server_side:optional","server_side:required"]]'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            response_formatted = response.json()

        mods = []
        for item in response_formatted.get("hits", []):
            project = {
                "project_id": item.get("project_id"),
                "author": item.get("author"),
                "description": item.get("description"),
                "icon_url": item.get("icon_url"),
                "title": item.get("title"),
                "server_side": item.get("server_side")
            }
            mods.append(project)

        result = {
            "total_hits": response_formatted.get("total_hits", 0),
            "limit": response_formatted.get("limit", limit),
            "offset": response_formatted.get("offset", offset),
            "results": mods
        }


        return result
    
    async def search_mod_version_game(self, project_id: str, mc_version: str = "1.21.1"):
        headers = {}
        if self.Authorization:
            headers["Authorization"] = self.Authorization

        async with httpx.AsyncClient() as client:
            project_url = f"{self.base_url}/project/{project_id}"
            project_response = await client.get(project_url, headers=headers)
            project_response.raise_for_status()
            project_data = project_response.json()

            files_url = f"{self.base_url}/project/{project_id}/version"
            params = {
                "loaders": '["fabric"]',
                "game_versions": f'["{mc_version}"]'
            }

            files_response = await client.get(files_url, headers=headers, params=params)
            files_response.raise_for_status()
            files = files_response.json()
        
        id_file_version, installed, ready = await files_service.FilesService().get_files_by_project_id(project_id=project_id)
    
        result = {
            "project_id": project_data.get("id"),
            "title": project_data.get("title"),
            "author": project_data.get("author"),
            "description": project_data.get("description"),
            "body": project_data.get("body"),
            "updated": project_data.get("updated"),
            "published": project_data.get("published"),
            "icon_url": project_data.get("icon_url"),
            "downloads": project_data.get("downloads", 0),
            "followers": project_data.get("followers", 0),
            "server_side": project_data.get("server_side"),
            "client_side": project_data.get("client_side"),
            "gallery": project_data.get("gallery", []),
            "file_version_id": id_file_version,
            "installed": installed,
            "ready": ready,
            "file_versions": files
        }

        return result
    
    async def recursive_dependencies(self, version_id: str, collected=None):
        if collected is None:
            collected = { "projects_ids" : [], "mods": [] }

        async with httpx.AsyncClient() as client:
            version_url = f"{self.base_url}/version/{version_id}"
            response = await client.get(version_url)
            response.raise_for_status()
            file = response.json()

        dependencies = file.get("dependencies", [])
        for dependency in dependencies:

            if dependency.get("dependency_type") == "required":
                dependency_project_id = dependency.get("project_id")
                
                if dependency_project_id:
                    existing_mod = next((mod for mod in collected["mods"] if mod["project_id"] == dependency_project_id), None)
                    
                    if existing_mod:
                        if version_id not in existing_mod["dependency_of"]:
                            existing_mod["dependency_of"].append(version_id)
                    else:
                        collected["projects_ids"].append(dependency_project_id)
                        
                        project = await self.search_mod_version_game(project_id=dependency_project_id)
                        mod_data = {
                            "id": project.get("file_versions")[0].get("id"),
                            "title": project.get("title"),
                            "description": project.get("description"),
                            "icon_url": project.get("icon_url"),
                            "download_url": project.get("file_versions")[0]["files"][0].get("url"),
                            "project_id": dependency_project_id,
                            "file_name": project.get("file_versions")[0]["files"][0].get("filename"),
                            "dependency_of": [version_id]
                        }

                        collected["mods"].append(mod_data)
                        await self.recursive_dependencies(version_id=project.get("file_versions")[0].get("id"), collected=collected)
        
        return collected

        
