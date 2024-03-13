from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from tekst.models.common import ModelBase
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase, ResourceSearchQueryBase
from tekst.models.resource_configs import (
    DeepLLinksConfig,
    DefaultCollapsedConfigType,
    FontConfigType,
    ReducedViewOnelineConfigType,
    ResourceConfigBase,
)
from tekst.resources import ResourceTypeABC
from tekst.utils import validators as val


class PlainText(ResourceTypeABC):
    """A simple plain text resource type"""

    @classmethod
    def resource_model(cls) -> type["PlainTextResource"]:
        return PlainTextResource

    @classmethod
    def content_model(cls) -> type["PlainTextContent"]:
        return PlainTextContent

    @classmethod
    def search_query_model(cls) -> type["PlainTextSearchRequest"]:
        return PlainTextSearchRequest

    @classmethod
    def index_doc_properties(cls) -> dict[str, Any]:
        return {
            "text": {
                "type": "text",
                "analyzer": "standard_asciifolding",
                "fields": {"strict": {"type": "text"}},
            },
        }

    @classmethod
    def index_doc_data(cls, content: "PlainTextContent") -> dict[str, Any]:
        return content.model_dump(include={"text"})


class GeneralPlainTextResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    reduced_view_oneline: ReducedViewOnelineConfigType = False
    font: FontConfigType = None


class PlainTextResourceConfig(ResourceConfigBase):
    general: GeneralPlainTextResourceConfig = GeneralPlainTextResourceConfig()
    deepl_links: DeepLLinksConfig = DeepLLinksConfig()


class PlainTextResource(ResourceBase):
    resource_type: Literal["plainText"]  # camelCased resource type classname
    config: PlainTextResourceConfig = PlainTextResourceConfig()


class PlainTextContent(ContentBase):
    """A content of a plain text resource"""

    resource_type: Literal["plainText"]  # camelCased resource type classname
    text: Annotated[
        str,
        StringConstraints(min_length=1, max_length=102400, strip_whitespace=True),
        Field(
            description="Text content of the plain text content object",
        ),
    ]


class PlainTextSearchRequest(ResourceSearchQueryBase):
    text: Annotated[
        str | None,
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = None
    comment: Annotated[
        str | None,
        StringConstraints(max_length=512, strip_whitespace=True),
        val.CleanupOneline,
    ] = None
