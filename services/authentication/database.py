from pymongo import MongoClient
import os
from typing import Optional, Annotated
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://auth-db:27017")

client = MongoClient(DATABASE_URL)
db = client.auth_db

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