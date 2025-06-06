from typing import Annotated

from pydantic import Field

from tekst.i18n import TranslationBase, Translations
from tekst.models.common import ModelBase
from tekst.models.platform import OskKey
from tekst.types import (
    CollapsibleContentsConfigValue,
    ConStr,
    ConStrOrNone,
    FontFamilyValueOrNone,
    SchemaOptionalNonNullable,
)


class GeneralResourceConfig(ModelBase):
    category: Annotated[
        ConStrOrNone(
            max_length=16,
        ),
        Field(
            description="Resource category key",
        ),
    ] = None
    sort_order: Annotated[
        int,
        Field(
            description="Sort order for displaying this resource among others",
            ge=0,
            le=1000,
        ),
    ] = 10
    default_active: Annotated[
        bool,
        Field(
            description="Whether this resource is active by default when public",
        ),
        SchemaOptionalNonNullable,
    ] = True
    collapsible_contents: CollapsibleContentsConfigValue = None
    font: FontFamilyValueOrNone = None
    enable_content_context: Annotated[
        bool,
        Field(
            description="Show combined contents of this resource on the parent level",
        ),
        SchemaOptionalNonNullable,
    ] = False
    show_comments: Annotated[
        bool,
        Field(
            description="Show authors/editors comments by default (if any)",
        ),
        SchemaOptionalNonNullable,
    ] = False
    searchable_quick: Annotated[
        bool,
        Field(
            description="Whether this resource should be included in quick search",
        ),
        SchemaOptionalNonNullable,
    ] = True
    searchable_adv: Annotated[
        bool,
        Field(
            description="Whether this resource should accessible via advanced search",
        ),
        SchemaOptionalNonNullable,
    ] = True
    rtl: Annotated[
        bool,
        Field(
            description="Whether to display text contents in right-to-left direction",
        ),
        SchemaOptionalNonNullable,
    ] = False
    osk: OskKey | None = None


class ResourceConfigBase(ModelBase):
    general: GeneralResourceConfig = GeneralResourceConfig()
    special: ModelBase | None = None


# GENERIC RESOURCE CONFIG: ITEM DISPLAY (ORDER, GROUPING AND TRANSLATIONS)


class ItemsDisplayTranslation(TranslationBase):
    translation: Annotated[
        ConStr(
            max_length=128,
            cleanup="oneline",
        ),
        Field(
            description="Translation of an item or item group name",
        ),
    ]


type ItemKey = Annotated[
    ConStr(max_length=32, cleanup="oneline"), Field(description="Key of an item")
]

type ItemGroupKey = Annotated[
    ConStr(max_length=32, cleanup="oneline"), Field(description="Key of an item group")
]


class ItemGroup(ModelBase):
    key: ItemGroupKey
    translations: Annotated[
        Translations[ItemsDisplayTranslation],
        Field(description="Translations for the name of the item group"),
    ]


class ItemProps(ModelBase):
    key: ItemKey
    translations: Annotated[
        Translations[ItemsDisplayTranslation],
        Field(description="Translations for the name of the item"),
    ]
    group: ItemGroupKey | None = None


class ItemIntegrationConfig(ModelBase):
    """Config for item ordering, grouping and translation"""

    groups: Annotated[
        list[ItemGroup],
        Field(
            description="Item groups",
            max_length=64,
        ),
    ] = []
    item_props: Annotated[
        list[ItemProps],
        Field(
            description="Item properties",
            max_length=128,
        ),
    ] = []

    def sorted_item_keys(
        self,
        item_keys: list[ItemKey] | None = None,
    ) -> list[ItemKey]:
        if item_keys is None:
            item_keys = [props.key for props in self.item_props]
        # get order of metadata groups from config
        groups_order = [g.key for g in self.groups]
        # sort keys based on groups order, then general keys order
        keys_order = sorted(
            self.item_props,
            key=lambda k: (
                groups_order.index(k.group)
                if k.group in groups_order
                else len(groups_order),
                self.item_props.index(k),
            ),
        )
        keys_order = [k.key for k in keys_order]
        # create final sorted list of metadata keys, including keys
        # that are not present in the item_props
        return sorted(
            item_keys,
            key=lambda k: (
                keys_order.index(k) if k in keys_order else len(keys_order),
                k,  # alphabetical secondary sorting
            ),
        )
