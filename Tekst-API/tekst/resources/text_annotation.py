import csv

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BeforeValidator, Field, StringConstraints, field_validator
from typing_extensions import TypeAliasType

from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import ModelBase, PrecomputedDataDocument
from tekst.models.content import ContentBase, ContentBaseDocument
from tekst.models.resource import (
    ResourceBase,
    ResourceExportFormat,
)
from tekst.models.resource_configs import (
    DefaultCollapsedConfigType,
    FontConfigType,
    ResourceConfigBase,
)
from tekst.models.text import TextDocument
from tekst.resources import ResourceBaseDocument, ResourceSearchQuery, ResourceTypeABC
from tekst.utils import validators as val


class TextAnnotation(ResourceTypeABC):
    """An annotation resource type for tokenized text"""

    @classmethod
    def resource_model(cls) -> type["TextAnnotationResource"]:
        return TextAnnotationResource

    @classmethod
    def content_model(cls) -> type["TextAnnotationContent"]:
        return TextAnnotationContent

    @classmethod
    def search_query_model(cls) -> type["TextAnnotationSearchQuery"]:
        return TextAnnotationSearchQuery

    @classmethod
    def rtype_index_doc_props(cls) -> dict[str, Any]:
        return {
            "tokens": {
                "type": "nested",
                "properties": {
                    "token": {
                        "type": "keyword",
                        "normalizer": "no_diacritics_normalizer",
                        "fields": {"strict": {"type": "keyword"}},
                    },
                    "annotations": {
                        "type": "nested",
                        "properties": {
                            "key": {
                                "type": "keyword",
                            },
                            "value": {
                                "type": "keyword",
                                "normalizer": "no_diacritics_normalizer",
                                "fields": {"strict": {"type": "keyword"}},
                            },
                        },
                    },
                },
            },
        }

    @classmethod
    def rtype_index_doc_data(
        cls,
        content: "TextAnnotationContent",
    ) -> dict[str, Any]:
        return {
            "tokens": [
                {
                    "token": token.token or "",
                    "annotations": [
                        {
                            "key": anno.key,
                            "value": anno.value[0]
                            if len(anno.value) == 1
                            else anno.value,
                        }
                        for anno in token.annotations
                    ]
                    if token.annotations
                    else None,
                }
                for token in content.tokens
            ],
        }

    @classmethod
    def rtype_es_queries(
        cls,
        *,
        query: ResourceSearchQuery,
        strict: bool = False,
    ) -> list[dict[str, Any]]:
        es_queries = []
        strict_suffix = ".strict" if strict else ""
        res_id = str(query.common.resource_id)
        q_id = str(uuid4())

        token_usr_q = (query.resource_type_specific.token or "").strip(" ") or None
        token_es_q = []
        annos_usr_q = query.resource_type_specific.annotations or []
        annos_es_q = []

        # process token query
        if (token_usr_q == "*" or not token_usr_q) and not annos_usr_q:
            # handle empty/match-all query (query for existing target resource field)
            token_es_q.append(
                {
                    "exists": {
                        "field": f"resources.{res_id}.tokens.token",
                    }
                }
            )
        elif token_usr_q:
            # handle actual token query with content
            token_es_q.append(
                {
                    "simple_query_string": {
                        "fields": [f"resources.{res_id}.tokens.token{strict_suffix}"],
                        "query": token_usr_q,
                        "analyze_wildcard": True,
                    }
                }
            )

        # process annotation queries
        for anno_q in annos_usr_q:
            if anno_q.key and not anno_q.value:
                # only key is set (and no value): query for existence of key
                anno_k_q = {
                    "term": {f"resources.{res_id}.tokens.annotations.key": anno_q.key}
                }
                annos_es_q.append(
                    {
                        "nested": {
                            "path": f"resources.{res_id}.tokens.annotations",
                            "query": anno_k_q,
                        }
                    }
                )
            elif anno_q.key and anno_q.value:
                # both key and value are set: query for specific key/value combination
                anno_k_q = {
                    "term": {f"resources.{res_id}.tokens.annotations.key": anno_q.key}
                }
                anno_v_q = {
                    "simple_query_string": {
                        "fields": [
                            (
                                f"resources.{res_id}.tokens.annotations"
                                f".value{strict_suffix}"
                            ),
                        ],
                        "query": anno_q.value,
                        "analyze_wildcard": True,
                    }
                }
                annos_es_q.append(
                    {
                        "nested": {
                            "path": f"resources.{res_id}.tokens.annotations",
                            "query": {
                                "bool": {
                                    "must": [anno_k_q, anno_v_q],
                                },
                            },
                        }
                    }
                )

        # add token and annotation queries to the ES queries
        if token_es_q or annos_es_q:
            es_sub_queries = [*token_es_q, *annos_es_q]
            es_queries.append(
                {
                    "nested": {
                        "path": f"resources.{res_id}.tokens",
                        "inner_hits": {"name": q_id},
                        "query": {
                            "bool": {
                                "must": es_sub_queries,
                            },
                        }
                        if len(es_sub_queries) > 1
                        else es_sub_queries[0],
                    }
                }
            )

        return es_queries

    @classmethod
    def highlights_generator(cls) -> Callable[[dict[str, Any]], list[str]] | None:
        def _highlights_generator(hit: dict[str, Any]) -> list[str]:
            hl_strings = []
            for hl_k, hl_v in hit["highlight"].items():
                if ".comment" in hl_k:
                    hl_strings.extend(hl_v)
            for ih in hit.get("inner_hits", {}).values():
                for ih_hit in ih.get("hits", {}).get("hits", []):
                    token = ih_hit["_source"]["token"]
                    annos = ih_hit["_source"]["annotations"]
                    annos = (
                        f" ({'; '.join([a['value'] for a in annos])})" if annos else ""
                    )
                    hl_strings.append(f"{token} {annos}")
            return hl_strings

        return _highlights_generator

    @classmethod
    async def export(
        cls,
        *,
        resource: ResourceBaseDocument,
        contents: list["TextAnnotationContent"],
        export_format: ResourceExportFormat,
        file_path: Path,
    ) -> None:
        if export_format == "csv":
            await cls._export_csv(resource, contents, file_path)
        else:
            raise ValueError(
                f"Unsupported export format '{export_format}' "
                f"for resource type '{cls.get_key()}'"
            )

    @classmethod
    async def _export_csv(
        cls,
        resource: "TextAnnotationResource",
        contents: list["TextAnnotationContent"],
        file_path: Path,
    ) -> None:
        text = await TextDocument.get(resource.text_id)
        # construct labels of all locations on the resource's level
        full_location_labels = await text.full_location_labels(resource.level)
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(
                csvfile,
                dialect="excel",
                quoting=csv.QUOTE_ALL,
            )
            anno_keys = sorted(list({agg.key for agg in resource.aggregations}))
            csv_writer.writerow(
                ["LOCATION", "TOKEN", "POSITION", *anno_keys, "COMMENT"]
            )
            for content in contents:
                for i, token in enumerate(content.tokens):
                    token_annos = {
                        anno.key: anno.value for anno in token.annotations or []
                    }
                    csv_annos = [
                        resource.config.multi_value_delimiter.join(
                            token_annos.get(anno_key, [])
                        )
                        for anno_key in anno_keys
                    ]
                    csv_writer.writerow(
                        [
                            full_location_labels.get(str(content.location_id), ""),
                            token.token,
                            i,
                            *csv_annos,
                            content.comment,
                        ]
                    )


class GeneralTextAnnotationResourceConfig(ModelBase):
    default_collapsed: DefaultCollapsedConfigType = False
    font: FontConfigType = None


class TextAnnotationResourceConfig(ResourceConfigBase):
    general: GeneralTextAnnotationResourceConfig = GeneralTextAnnotationResourceConfig()
    display_template: Annotated[
        str | None,
        Field(
            max_length=2048,
            description=(
                "Template string used for displaying the annotations in the web client "
                "(if missing, all annotations are displayed with key and value, "
                "separated by commas)"
            ),
        ),
        val.CleanupMultiline,
        val.EmptyStringToNone,
    ] = None
    multi_value_delimiter: Annotated[
        str,
        Field(
            description="String used to delimit multiple values for an annotation",
        ),
        StringConstraints(min_length=1, max_length=3, strip_whitespace=True),
    ] = "/"


class AnnotationAggregation(ModelBase):
    key: str
    values: list[str] | None = None


class TextAnnotationResource(ResourceBase):
    resource_type: Literal["textAnnotation"]  # camelCased resource type classname
    config: TextAnnotationResourceConfig = TextAnnotationResourceConfig()

    @classmethod
    def quick_search_fields(cls) -> list[str]:
        return ["tokens.token", "tokens.annotations.value"]

    async def _update_aggregations(self) -> None:
        # get precomputed resource aggregations data, if present
        precomp_doc = await PrecomputedDataDocument.find_one(
            PrecomputedDataDocument.ref_id == self.id,
            PrecomputedDataDocument.precomputed_type == "aggregations",
        )
        if precomp_doc:
            if precomp_doc.created_at > self.contents_changed_at:
                log.debug(
                    f"Aggregations for resource {str(self.id)} up-to-date. Skipping."
                )
                return
        else:
            # create new aggregations document
            precomp_doc = PrecomputedDataDocument(
                ref_id=self.id,
                precomputed_type="aggregations",
            )

        # group annotations
        precomp_doc.data = (
            await ContentBaseDocument.find(
                ContentBaseDocument.resource_id == self.id,
                with_children=True,
            )
            .aggregate(
                [
                    {"$project": {"anno": "$tokens.annotations"}},
                    {"$unwind": {"path": "$anno"}},
                    {"$unwind": {"path": "$anno"}},
                    {"$unwind": {"path": "$anno.value"}},
                    # create one document for each annotation key,
                    # collecting all values and the key occurrence count
                    {
                        "$group": {
                            "_id": "$anno.key",
                            "values": {"$push": "$anno.value"},
                            "keyOcc": {"$sum": 1},
                        }
                    },
                    # count per-key value occurrences on "values" field
                    {
                        "$set": {
                            "values": {
                                "$map": {
                                    "input": {"$setUnion": "$values"},
                                    "as": "v",
                                    "in": {
                                        "value": "$$v",
                                        "count": {
                                            "$size": {
                                                "$filter": {
                                                    "input": "$values",
                                                    "cond": {"$eq": ["$$this", "$$v"]},
                                                }
                                            }
                                        },
                                    },
                                }
                            }
                        }
                    },
                    # remove values array if it contains more than 100 items
                    {
                        "$set": {
                            "values": {
                                "$cond": {
                                    "if": {"$gt": [{"$size": "$values"}, 100]},
                                    "then": "$$REMOVE",
                                    "else": "$values",
                                }
                            }
                        }
                    },
                    # sort values array by count
                    {
                        "$set": {
                            "values": {
                                "$sortArray": {
                                    "input": "$values",
                                    "sortBy": {"count": -1},
                                }
                            }
                        }
                    },
                    # sort docs by key occurrence
                    {"$sort": {"keyOcc": -1}},
                    # project to final doc format,
                    # with values array only containing the values
                    {
                        "$project": {
                            "_id": 0,
                            "key": "$_id",
                            "values": {
                                "$map": {
                                    "input": "$values",
                                    "as": "v",
                                    "in": "$$v.value",
                                }
                            },
                        }
                    },
                ]
            )
            .to_list()
        )

        # update aggregations in DB
        precomp_doc.created_at = datetime.utcnow()
        await precomp_doc.save()

    async def contents_changed_hook(self) -> None:
        await super().contents_changed_hook()

    async def resource_maintenance_hook(self) -> None:
        await super().resource_maintenance_hook()
        op_id = log_op_start(f"Generate aggregations for resource {str(self.id)}")
        try:
            await self._update_aggregations()
        except Exception as e:
            log_op_end(op_id, failed=True)
            raise e
        log_op_end(op_id)


TextAnnotationValue = TypeAliasType(
    "TextAnnotationValue",
    Annotated[
        str,
        Field(
            description="Value of an annotation",
        ),
        BeforeValidator(lambda v: str(v) if v is not None else None),
        StringConstraints(
            min_length=1,
            max_length=256,
            strip_whitespace=True,
        ),
    ],
)

TextAnnotationValues = TypeAliasType(
    "TextAnnotationValues",
    Annotated[
        list[TextAnnotationValue],
        Field(
            description="List of values of an annotation",
            min_length=1,
            max_length=64,
        ),
        BeforeValidator(lambda v: [v] if isinstance(v, str) else v),
    ],
)


class TextAnnotationEntry(ModelBase):
    key: Annotated[
        str,
        Field(
            description="Key of the annotation",
        ),
        BeforeValidator(lambda v: str(v) if v is not None else None),
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    value: Annotated[
        TextAnnotationValues,
        Field(
            description="Value(s) of the annotation",
        ),
    ]


class TextAnnotationQueryEntry(ModelBase):
    key: Annotated[
        str,
        Field(
            alias="k",
            description="Key of the annotation",
        ),
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
    ]
    value: Annotated[
        str | None,
        Field(
            alias="v",
            description="Value of the annotation",
        ),
        StringConstraints(
            max_length=64,
            strip_whitespace=True,
        ),
    ] = None

    @field_validator("key", "value", mode="before")
    @classmethod
    def strip_whitespace(cls, v) -> str:
        return str(v) if v else ""


class TextAnnotationToken(ModelBase):
    token: Annotated[
        str,
        Field(
            description="Text token",
        ),
        StringConstraints(
            min_length=1,
            max_length=4096,
            strip_whitespace=True,
        ),
    ]
    annotations: Annotated[
        list[TextAnnotationEntry],
        Field(
            description="List of annotations on this token",
            max_length=128,
        ),
    ] = []
    lb: Annotated[
        bool,
        Field(description="Whether this token ends a line"),
    ] = False


class TextAnnotationContent(ContentBase):
    """A content of a text annotation resource"""

    resource_type: Literal["textAnnotation"]  # camelCased resource type classname
    tokens: Annotated[
        list[TextAnnotationToken],
        Field(
            description="List of annotated tokens in this content object",
            max_length=1024,
        ),
    ]


class TextAnnotationSearchQuery(ModelBase):
    resource_type: Annotated[
        Literal["textAnnotation"],
        Field(
            alias="type",
            description="Type of the resource to search in",
        ),
    ]
    token: Annotated[
        str,
        StringConstraints(
            max_length=512,
            strip_whitespace=True,
        ),
        val.CleanupOneline,
    ] = ""
    annotations: Annotated[
        list[TextAnnotationQueryEntry],
        Field(
            alias="anno",
            description="List of annotations to match",
            max_length=64,
        ),
    ] = []
