from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from controllers.modrinth.modrinth_controller import router as modrinth_router, set_modrinth_authorization
from controllers.files.files_controller import router as files_router
from controllers.mods.mods_controller import router as mods_router
from controllers.mc_server.mc_server_controller import router as mc_server_router
import os

app = FastAPI(title="Minecraft Backend API")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

@app.middleware("http")
async def verify_origin(request: Request, call_next):
    client_host = request.client.host if request.client else None
    if client_host and (
        client_host.startswith("172.") or 
        client_host.startswith("192.168.") or 
        client_host in ["127.0.0.1", "localhost"]
    ):
        return await call_next(request)
    
    raise HTTPException(status_code=403, detail="Forbidden: External access not allowed")

# CORS apenas para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

set_modrinth_authorization(os.getenv("MODRINTH_AUTHORIZATION", ""))
app.include_router(modrinth_router)
app.include_router(files_router)
app.include_router(mc_server_router)
app.include_router(mods_router)

@app.get("/")
async def root():
    return {"message": "Minecraft Backend API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)