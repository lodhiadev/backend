from fastapi import APIRouter, HTTPException
from app.models import AdminLogin
from app.db import master_db
from app.utils import verify_password, create_access_token
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()

@router.post("/login")
async def admin_login(payload: AdminLogin):
    org = await master_db.organizations.find_one({"admin.email": payload.email})
    if not org:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    stored_hash = org["admin"]["password_hash"]
    if not verify_password(payload.password, stored_hash):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": payload.email, "org": org["organization_name"]})
    return {"access_token": token, "token_type": "bearer"}
