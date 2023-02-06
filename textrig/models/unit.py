# from fastapi import HTTPException, status
from pydantic import Field

# from textrig.db.io import DbIO
# from textrig.logging import log
from textrig.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    PyObjectId,
    UpdateBase,
)


class UnitBase(ModelBase):
    """A base class for types of data units belonging to a certain data layer"""

    layer_id: PyObjectId = Field(..., description="Data layer ID")
    node_id: PyObjectId = Field(..., description="Parent text node ID")
    meta: Metadata | None = Field(
        None,
        description="Arbitrary metadata on this layer unit",
    )

    __template_fields: tuple[str] = ("meta",)

    class Settings:
        name = "units"
        is_root = True

    @classmethod
    def get_layer_type_plugin_class(cls) -> type:
        raise NotImplementedError(
            "Method UnitBase.get_layer_type_plugin_class must be overridden!"
        )

    @classmethod
    def get_template_fields(cls) -> tuple[str]:
        return cls.__template_fields + getattr(cls, "_template_fields", tuple())


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class UnitBaseDocument(UnitBase, DocumentBase):
    pass


class UnitBaseUpdate(UnitBase, UpdateBase):
    pass
