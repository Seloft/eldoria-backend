import docker
import asyncio
from concurrent.futures import ThreadPoolExecutor

class DockerService:
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def get_container(self, container_name):
        try:
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                self.executor,
                self.docker_client.containers.get,
                container_name
            )
            return container
        except docker.errors.NotFound:
            print(f"Container {container_name} not found.")
            return None
        except Exception as e:
            print(f"Error retrieving container {container_name}: {e}")
            return None
        
    async def restart_container(self, container_name):
        try:
            container = await self.get_container(container_name)
            if container:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    container.restart
                )
                return True
            return False
        
        except Exception as e:
            print(f"Error restarting container {container_name}: {e}")
            return False
        
    async def stop_container(self, container_name):
        try:
            container = await self.get_container(container_name)
            if container:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self.executor,
                    container.stop
                )
                return True
            return False
        
        except Exception as e:
            print(f"Error stopping container {container_name}: {e}")
            return False
        
    async def start_container(self, container_name):
        try:
            container = await self.get_container(container_name)
            if container:
                await container.start()
                return True
            return False
        
        except Exception as e:
            print(f"Error starting container {container_name}: {e}")
            return False
        
    async def exec_in_container(self, container_name: str, command: str, binary: bool = False):
        try:
            loop = asyncio.get_event_loop()
            
            def _exec():
                container = self.docker_client.containers.get(container_name)
                result = container.exec_run(command)
                return result.exit_code, result.output
            
            exit_code, output = await loop.run_in_executor(self.executor, _exec)
            
            if binary:
                return exit_code, output
            
            if isinstance(output, bytes):
                output = output.decode('utf-8')
            
            return exit_code, output
        except Exception as e:
            print(f"Error executing command in container {container_name}: {e}")
            return 1, None
        
    async def get_current_timestamp(self):
        import time
        return int(time.time())