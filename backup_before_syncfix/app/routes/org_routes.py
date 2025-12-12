from fastapi import APIRouter, HTTPException, Depends
from app.db import master_db
from app.models import OrgCreate
from app.utils import hash_password
from starlette.status import HTTP_201_CREATED
import re

router = APIRouter()

def collection_name_for_org(name: str) -> str:
    # sanitize and enforce pattern: org_<sanitizedname>
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    return f"org_{sanitized}"

@router.post("/create", status_code=HTTP_201_CREATED)
async def create_org(payload: OrgCreate):
    org_name = payload.organization_name.strip()
    if not org_name:
        raise HTTPException(status_code=400, detail="organization_name required")

    # check master db for uniqueness
    existing = await master_db.organizations.find_one({"organization_name": org_name})
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")

    collection_name = collection_name_for_org(org_name)
    # Create admin user record
    hashed = hash_password(payload.password)
    admin_doc = {
        "email": payload.email,
        "password_hash": hashed
    }
    org_doc = {
        "organization_name": org_name,
        "collection_name": collection_name,
        "admin": admin_doc
    }
    # Insert into master db
    res = await master_db.organizations.insert_one(org_doc)
    return {
        "organization_name": org_name,
        "collection_name": collection_name,
        "id": str(res.inserted_id)
    }

@router.get("/get")
async def get_org(organization_name: str):
    org = await master_db.organizations.find_one({"organization_name": organization_name}, {"_id":0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/update")
async def update_org(payload: OrgCreate):
    org_name = payload.organization_name.strip()
    org = await master_db.organizations.find_one({"organization_name": org_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    new_collection = collection_name_for_org(org_name)
    await master_db.organizations.update_one({"organization_name": org_name}, {"$set": {
        "collection_name": new_collection,
        "admin.email": payload.email,
        "admin.password_hash": hash_password(payload.password)
    }})
    return {"detail":"Organization updated"}

@router.delete("/delete")
async def delete_org(organization_name: str, admin_email: str):
    org = await master_db.organizations.find_one({"organization_name": organization_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    col_name = org["collection_name"]
    # drop collection - motor uses client to access db
    db = master_db.client[master_db.name]
    if col_name in await db.list_collection_names():
        await db.drop_collection(col_name)
    await master_db.organizations.delete_one({"organization_name": organization_name})
    return {"detail":"Organization deleted"}
