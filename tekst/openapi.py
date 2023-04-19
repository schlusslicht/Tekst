from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from tekst.config import TekstConfig


tags_metadata = [
    {
        "name": "texts",
        "description": "Text-related operations",
        "externalDocs": {
            "description": "View external documentation",
            "url": "https://github.com/VedaWebProject/tekst-api",
        },
    },
]


def process_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    # nothing happening here, yet
    return schema


def custom_openapi(app: FastAPI, cfg: TekstConfig):
    def _custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=cfg.info.platform_name,
            version=cfg.tekst_info.version,
            description=cfg.info.description,
            routes=app.routes,
            servers=[{"url": urljoin(cfg.server_url, cfg.api_path)}],
            terms_of_service=cfg.info.terms,
            tags=tags_metadata,
            contact={
                "name": cfg.info.contact_name,
                "url": cfg.info.contact_url,
                "email": cfg.info.contact_email,
            },
            license_info={
                "name": cfg.tekst_info.license,
                "url": cfg.tekst_info.license_url,
            },
        )
        app.openapi_schema = process_openapi_schema(openapi_schema)
        return app.openapi_schema

    app.openapi = _custom_openapi
