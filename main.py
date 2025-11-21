import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

app = FastAPI(title="Student Learning Resource Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility to convert Mongo _id to string
def serialize_doc(doc: dict) -> dict:
    if not doc:
        return doc
    d = {**doc}
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


@app.get("/")
def read_root():
    return {"message": "Student Learning Resource Platform Backend is running"}


@app.get("/api/health")
def api_health():
    return {"ok": True}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -------------------- Resources API --------------------
class CreateResource(BaseModel):
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    class_: Optional[str] = None
    exam: Optional[str] = None
    year: Optional[str] = None
    file_url: str
    thumbnail_url: Optional[str] = None
    type: Optional[str] = None
    uploader_id: Optional[str] = None


@app.get("/api/resources")
def list_resources(q: Optional[str] = None, subject: Optional[str] = None, type: Optional[str] = None, limit: int = 24):
    try:
        from database import db
        if db is None:
            raise HTTPException(status_code=500, detail="Database not configured")

        filter_query = {}
        if q:
            # Basic text-like search across fields
            filter_query["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"subject": {"$regex": q, "$options": "i"}},
                {"exam": {"$regex": q, "$options": "i"}},
                {"year": {"$regex": q, "$options": "i"}},
            ]
        if subject:
            filter_query["subject"] = subject
        if type:
            filter_query["type"] = type

        cursor = db["studyasset"].find(filter_query).sort("created_at", -1).limit(int(limit))
        items = [serialize_doc(doc) for doc in cursor]
        return {"items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resources")
def create_resource(payload: CreateResource):
    try:
        from database import create_document
        rid = create_document("studyasset", payload.model_dump(by_alias=True))
        return {"id": rid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resources/{resource_id}")
def get_resource(resource_id: str):
    try:
        from database import db
        if db is None:
            raise HTTPException(status_code=500, detail="Database not configured")
        try:
            oid = ObjectId(resource_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid id")
        doc = db["studyasset"].find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="Resource not found")
        return serialize_doc(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resources/{resource_id}/like")
def like_resource(resource_id: str):
    try:
        from database import db
        if db is None:
            raise HTTPException(status_code=500, detail="Database not configured")
        try:
            oid = ObjectId(resource_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid id")
        res = db["studyasset"].update_one({"_id": oid}, {"$inc": {"likes": 1}})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Resource not found")
        doc = db["studyasset"].find_one({"_id": oid})
        return serialize_doc(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
