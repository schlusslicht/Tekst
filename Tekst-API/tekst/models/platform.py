from typing import Annotated, Any

from beanie import PydanticObjectId
from humps import camelize
from pydantic import Field

from tekst.config import TekstConfig, get_config
from tekst.layer_types import LayerTypeInfo
from tekst.models.common import ModelBase
from tekst.models.segment import ClientSegment
from tekst.models.settings import PlatformSettingsRead
from tekst.models.text import TextRead


_cfg: TekstConfig = get_config()


class PlatformSecurityInfo(ModelBase):
    closed_mode: bool = _cfg.security_closed_mode
    users_active_by_default: bool = _cfg.security_users_active_by_default
    enable_cookie_auth: bool = _cfg.security_enable_cookie_auth
    enable_jwt_auth: bool = _cfg.security_enable_jwt_auth
    auth_cookie_lifetime: int = _cfg.security_auth_cookie_lifetime


class PlatformData(ModelBase):
    """Platform data used by the web client"""

    info: dict[str, Any] = camelize(
        _cfg.model_dump(include_keys_prefix="info_", strip_include_keys_prefix=True)
    )
    tekst: dict[str, Any] = camelize(
        _cfg.model_dump(include_keys_prefix="tekst_", strip_include_keys_prefix=True)
    )
    texts: list[TextRead]
    settings: PlatformSettingsRead
    security: PlatformSecurityInfo = PlatformSecurityInfo()
    layer_types: Annotated[list[LayerTypeInfo], Field(alias="layerTypes")]
    system_segments: Annotated[list[ClientSegment], Field(alias="systemSegments")]
    page_segment_keys: Annotated[list[str], Field(alias="pageSegmentKeys")]


class TextStats(ModelBase):
    """Text statistics data"""

    id: PydanticObjectId
    nodes_count: int
    layers_count: int
    layer_types: dict[str, int]


class PlatformStats(ModelBase):
    """Platform statistics data"""

    users_count: int
    texts: list[TextStats]
