"""
Database Schemas for Student Learning Resource Platform

Each Pydantic model corresponds to a MongoDB collection.
Collection name is the lowercase of the model class name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    avatar: Optional[str] = Field(None, description="Avatar image URL")
    bio: Optional[str] = Field(None, description="Short bio")
    createdAt: Optional[datetime] = Field(default=None, description="Creation timestamp")


class Studyasset(BaseModel):
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    class_: Optional[str] = Field(default=None, alias="class", description="Class/Grade")
    exam: Optional[str] = None
    year: Optional[str] = None
    file_url: str = Field(..., description="Public URL to the file")
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail image URL")
    type: Optional[str] = Field(default=None, description="Type like notes, past_paper, mind_map, etc.")
    uploader_id: Optional[str] = Field(default=None, description="User id of uploader")
    likes: int = Field(default=0)
    createdAt: Optional[datetime] = Field(default=None)


class Report(BaseModel):
    asset_id: str
    reporter_id: Optional[str] = None
    reason: str
    status: str = Field(default="open")
    createdAt: Optional[datetime] = None


class Like(BaseModel):
    user_id: str
    asset_id: str
    createdAt: Optional[datetime] = None
