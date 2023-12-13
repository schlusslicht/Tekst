from datetime import datetime
from typing import Annotated, Literal, get_args

import pymongo

from beanie import Document, PydanticObjectId
from fastapi_users import (
    schemas,
)
from fastapi_users_db_beanie import (
    BeanieBaseUser,
)
from pydantic import Field, StringConstraints, model_validator
from pymongo import IndexModel

from tekst.config import TekstConfig, get_config
from tekst.models.common import Locale, ModelBase, ModelFactoryMixin


_cfg: TekstConfig = get_config()

PublicUserField = Literal["name", "affiliation"]


class UserReadPublic(ModelBase):
    id: PydanticObjectId
    username: str
    name: str | None = None
    affiliation: str | None = None
    public_fields: Annotated[
        list[PublicUserField],
        Field(description="Data fields set public by this user", max_length=64),
    ] = []

    @model_validator(mode="after")
    def model_postprocess(self):
        for pf in get_args(PublicUserField):
            if pf not in self.public_fields:
                setattr(self, pf, None)
        return self


class User(ModelBase, ModelFactoryMixin):
    """This base model defines the custom fields added to FastAPI-User's user model"""

    username: Annotated[
        str, StringConstraints(min_length=4, max_length=16, pattern=r"[a-zA-Z0-9\-_]+")
    ]
    name: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    affiliation: Annotated[str, StringConstraints(min_length=1, max_length=64)]
    locale: Locale | None = None
    public_fields: Annotated[
        list[PublicUserField], Field(description="Data fields set public by this user")
    ] = []


class UserDocument(User, BeanieBaseUser, Document):
    """User document model used by FastAPI-Users"""

    class Settings(BeanieBaseUser.Settings):
        name = "users"
        indexes = BeanieBaseUser.Settings.indexes + [
            IndexModel("username", unique=True),
            IndexModel(
                [
                    ("username", pymongo.TEXT),
                    ("name", pymongo.TEXT),
                    ("affiliation", pymongo.TEXT),
                ],
            ),
        ]

    is_active: bool = _cfg.security_users_active_by_default
    created_at: datetime = datetime.utcnow()


class UserRead(User, schemas.BaseUser[PydanticObjectId]):
    """A user registered in the system"""

    # we redefine these fields here because they should be required in a read model
    # but have default values in FastAPI-User's schemas.BaseUser...
    id: PydanticObjectId
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime


class UserCreate(User, schemas.BaseUserCreate):
    """Dataset for creating a new user"""

    is_active: bool = _cfg.security_users_active_by_default


UserUpdate = User.update_model(schemas.BaseUserUpdate)
