from typing import Literal

from pydantic import Field, validator

from tekst.models.common import LayerConfigBase


class DeepLLinksConfig(LayerConfigBase):
    _DEEPL_LANGUAGES: tuple = (
        "BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI",
        "FR", "HU", "ID", "IT", "JA", "LT", "LV", "NL", "PL",
        "PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH",
    )  # fmt: skip

    enabled: bool = Field(
        False,
        description="Enable/disable quick translation links to DeepL",
    )
    source_language: Literal[_DEEPL_LANGUAGES] | None = Field(
        _DEEPL_LANGUAGES[0], description="Source language"
    )
    languages: list[Literal[_DEEPL_LANGUAGES]] = Field(
        ["EN", "DE"], description="Target languages to display links for"
    )

    @classmethod
    def _uppercase_lang_code(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise TypeError("Language codes have to be passed as strings")
        return v.upper()

    # validators
    _validate_source_language = validator(
        "source_language", pre=True, allow_reuse=True
    )(_uppercase_lang_code)
    _validate_languages = validator(
        "languages", pre=True, each_item=True, allow_reuse=True
    )(_uppercase_lang_code)
