from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import org_routes, admin_routes

app = FastAPI(title="Organization Management Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo; restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(org_routes.router, prefix="/org", tags=["org"])
app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
