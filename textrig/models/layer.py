import re

from pydantic import Field, validator
from textrig.models.common import AllOptional, DbDocument, Metadata, TextRigBaseModel


class Layer(TextRigBaseModel):
    """A data layer describing a set of data on a text"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this layer"
    )
    description: str = Field(
        None,
        min_length=1,
        max_length=128,
        description="Short, one-line description of this data layer",
    )
    text_slug: str = Field(..., description="Slug of the text this layer belongs to")
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(...)
    # owner_id: DocId = Field(None)  # TODO: users don't exist, yet
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    @validator("description")
    def handle_whitespaces_in_description(cls, v):
        return re.sub(r"\s+", " ", v)


class LayerRead(Layer, DbDocument):
    """An existing data layer read from the database"""

    ...


class LayerUpdate(Layer, metaclass=AllOptional):
    """An update to an existing data layer"""

    ...
