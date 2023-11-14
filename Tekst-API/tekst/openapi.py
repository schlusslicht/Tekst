from typing import Any
from urllib.parse import urljoin

from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi

from tekst.config import TekstConfig
from tekst.models.settings import PlatformSettingsRead


tags_metadata = [
    {
        "name": "texts",
        "description": "Text-related operations",
        "externalDocs": {
            "description": "View full documentation",
            "url": "https://vedawebproject.github.io/Tekst",
        },
    },
]


def customize_openapi(app: FastAPI, cfg: TekstConfig, settings: PlatformSettingsRead):
    def _custom_openapi():
        if not app.openapi_schema:
            app.openapi_schema = generate_schema(app, cfg, settings)
        return app.openapi_schema

    app.openapi = _custom_openapi


def generate_schema(app: FastAPI, cfg: TekstConfig, settings: PlatformSettingsRead):
    schema = get_openapi(
        title=settings.info_platform_name,
        version=cfg.tekst_version,
        description=settings.info_description,
        routes=app.routes,
        servers=[{"url": urljoin(str(cfg.server_url), str(cfg.api_path))}],
        terms_of_service=str(settings.info_terms),
        tags=tags_metadata,
        contact={
            "name": settings.info_contact_name,
            "url": settings.info_contact_url,
            "email": settings.info_contact_email,
        },
        license_info={
            "name": cfg.tekst_license,
            "url": cfg.tekst_license_url,
        },
    )
    return process_openapi_schema(schema)


def process_openapi_schema(schema: dict[str, Any]) -> dict[str, Any]:
    # nothing happening here, yet
    return schema


async def generate_openapi_schema(
    to_file: bool, output_file: str, indent: int, sort_keys: bool, cfg: TekstConfig
) -> str:
    """
    Atomic operation for creating and processing the OpenAPI schema from outside of
    the app context. This is used in __main__.py
    """

    import json

    from asgi_lifespan import LifespanManager
    from httpx import AsyncClient

    from tekst.app import app

    async with LifespanManager(app):  # noqa: SIM117
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get(f"{cfg.doc_openapi_url}")
            if resp.status_code != 200:
                raise HTTPException(resp.status_code)
            else:
                schema = resp.json()
                json_dump_args = {
                    "skipkeys": True,
                    "indent": indent or None,
                    "sort_keys": sort_keys,
                }
                if to_file:
                    with open(output_file, "w") as f:
                        json.dump(schema, f, **json_dump_args)
                return json.dumps(schema, **json_dump_args)
