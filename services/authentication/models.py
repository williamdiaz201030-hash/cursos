from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
import sys
sys.path.insert(0, '/app')

try:
    from database import PyObjectId
except ImportError:
    # Definir PyObjectId localmente si no se puede importar
    class PyObjectId(ObjectId):
        @classmethod
        def __get_pydantic_core_schema__(cls, _source_type, _handler):
            return core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    lambda instance: str(instance),
                    return_schema=core_schema.str_schema(),
                ),
            )

        @classmethod
        def validate(cls, v):
            if isinstance(v, ObjectId):
                return v
            if isinstance(v, str):
                try:
                    return ObjectId(v)
                except Exception:
                    raise ValueError("Invalid ObjectId")
            raise ValueError("ObjectId must be a string or ObjectId instance")

class UserBase(BaseModel):
    email: str
    full_name: str
    user_type: str  # "student" or "instructor"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None