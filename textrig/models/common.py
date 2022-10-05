from typing import Optional

from bson.objectid import InvalidId, ObjectId
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from pydantic.main import ModelMetaclass


def convert_field_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )


class PyObjectId(ObjectId):
    """A pydantic representation of MongoDB's object ID"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseModel(PydanticBaseModel):
    """Base class for all TextRig models"""

    def __init__(self, **kwargs):
        """Converts "_id" to "id" """
        if "_id" in kwargs and kwargs["_id"]:
            kwargs["id"] = kwargs.pop("_id")
        super().__init__(**kwargs)

    def dict(self, for_mongo: bool = False, **kwargs):
        parsed = super().dict(
            exclude_unset=kwargs.pop("exclude_unset", True),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

        if for_mongo and "_id" not in parsed and "id" in parsed:
            parsed["_id"] = parsed.pop("id")

        return parsed

    class Config:
        alias_generator = convert_field_to_camel_case


class ObjectInDB(PydanticBaseModel):
    """Data model mixin for objects from the DB (which have an ID)"""

    id: PyObjectId = Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: lambda oid: str(oid)}


class AllOptional(ModelMetaclass):
    """
    Metaclass to render all fields of a pydantic model optional (on root level).
    This approach was taken from here:
    https://stackoverflow.com/a/67733889/7399631
    Alternative ones are discussed here:
    https://github.com/pydantic/pydantic/issues/1223#issuecomment-998160737
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)
