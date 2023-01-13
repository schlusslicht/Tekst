# import json
# from tempfile import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, status

# from fastapi.responses import FileResponse
# from starlette.background import BackgroundTask
from textrig.db import from_mongo

# from textrig.dependencies import get_db_io
from textrig.layer_types import get_layer_types

# from textrig.logging import log
from textrig.models.layer import LayerBase, LayerUpdateBase


# from textrig.utils.strings import safe_name


def _generate_read_endpoint(layer_read_model: type[LayerBase]):
    async def get_layer(layer_id: str) -> layer_read_model:
        """A generic route for reading a layer definition from the database"""
        return await layer_read_model.get(layer_id)

    return get_layer


def _generate_create_endpoint(
    layer_model: type[LayerBase],
):
    async def create_layer(layer: layer_model) -> layer_model:
        return await layer.create()

    return create_layer


def _generate_update_endpoint(
    layer_update_model: type[LayerUpdateBase],
    layer_model: type[LayerBase],
):
    async def update_layer(layer_update: layer_update_model) -> layer_model:
        layer: layer_model = await layer_model.get(layer_update.id)
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer with ID {layer_update.id} could not be found",
            )
        await layer.set(layer_update.dict(exclude_unset=True))
        return layer

    return update_layer


router = APIRouter(
    prefix="/layers",
    tags=["layers"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
    },
)


# dynamically add all needed routes for every layer type's layer definitions
for lt_name, lt_class in get_layer_types().items():
    # add route for reading a layer definition from the database
    router.add_api_route(
        path=f"/{lt_name}/{{layer_id}}",
        name=f"get_{lt_name}_layer",
        description=f"Returns the data for a {lt_class.get_name()} data layer",
        endpoint=_generate_read_endpoint(lt_class.get_layer_model()),
        methods=["GET"],
        response_model=lt_class.get_layer_model(),
        status_code=status.HTTP_200_OK,
    )
    # add route for creating a layer
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"create_{lt_name}_layer",
        description=f"Creates a {lt_class.get_name()} data layer definition",
        endpoint=_generate_create_endpoint(
            lt_class.get_layer_model(),
        ),
        methods=["POST"],
        response_model=lt_class.get_layer_model(),
        status_code=status.HTTP_201_CREATED,
    )
    # add route for updating a layer
    router.add_api_route(
        path=f"/{lt_name}",
        name=f"update_{lt_name}_layer",
        description=f"Updates the data for a {lt_class.get_name()} data layer",
        endpoint=_generate_update_endpoint(
            lt_class.get_layer_update_model(),
            lt_class.get_layer_model(),
        ),
        methods=["PATCH"],
        response_model=lt_class.get_layer_model(),
        status_code=status.HTTP_200_OK,
    )


# ADDITIONAL ROUTE DEFINITIONS...


@router.get("", response_model=list[dict], status_code=status.HTTP_200_OK)
async def get_layers(
    text_slug: str,
    level: int = None,
    layer_type: str = None,
    limit: int = 1000,
) -> list:

    example = dict(text_slug=text_slug)

    if level is not None:
        example["level"] = level

    if layer_type is not None:
        example["layer_type"] = layer_type

    # return from_mongo(await db_io.find("layers", example=example, limit=limit))
    return from_mongo(
        await LayerBase.find(example, limit=limit, with_children=True).to_list()
    )


# @router.post("", response_model=LayerReadBase, status_code=status.HTTP_201_CREATED)
# async def create_layer(
#     layer: LayerBase, db_io: DbIO = Depends(get_db_io)
# ) -> LayerReadBase:
#     if not await db_io.find_one("texts", layer.text_slug, "slug"):
#         raise HTTPException(
#             status.HTTP_400_BAD_REQUEST, detail="Corresponding text doesn't exist"
#         )
#     layer = await db_io.insert_one("layers", layer)
#     log.debug(f"Created layer: {layer}")
#     return layer


#
#   TODO: rebuild template endpoint using beanie logic
#

# @router.get("/template", status_code=status.HTTP_200_OK)
# async def get_layer_template(layer_id: str, db_io: DbIO = Depends(get_db_io)) -> dict:
#     layer_data = await db_io.find_one("layers", layer_id)

#     if not layer_data:
#         raise HTTPException(
#             status.HTTP_400_BAD_REQUEST,
#             detail=f"Layer with ID {layer_id} doesn't exist",
#         )

#     # decode layer data: Usually, this is handled automatically by our models, but
#     # in this case we're returning a raw dict/JSON, so we have to manually make sure
#     # that a) the ID field is called "id" and b) the DocumentId value is encoded as str.
#     layer_read_model = get_layer_type(layer_data["layerType"]).get_layer_read_model()
#     layer_data = layer_read_model(**layer_data).dict()

#     # import unit type for the requested layer
#     template = get_layer_type(layer_data["layerType"]).prepare_import_template()
#     # apply data from layer instance
#     template["layerId"] = str(layer_data["id"])
#     template["_level"] = layer_data["level"]
#     template["_title"] = layer_data["title"]
#     template["_description"] = layer_data.get("description", None)

#     # generate unit template
#     node_template = {key: None for key in template["_unitSchema"].keys()}

#     # get IDs of all nodes on this structure level as a base for unit templates
#     nodes = await db_io.find(
#         "nodes",
#         example={"textSlug": layer_data["textSlug"], "level": layer_data["level"]},
#         projection={"_id", "label"},
#         limit=0,
#     )

#     # fill in unit templates with IDs
#     template["units"] = [
#         dict(nodeId=str(node["_id"]), **node_template) for node in nodes
#     ]

#     # create temporary file and stream it as a file response
#     tempfile = NamedTemporaryFile(mode="w")
#     tempfile.write(json.dumps(template, indent=2))
#     tempfile.flush()

#     # prepare headers
#     filename = (
#         f"{layer_data['textSlug']}_layer_{safe_name(template['layerId'])}"
#         "_template.json"
#     )
#     headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

#     log.debug(f"Serving layer template as temporary file {tempfile.name}")
#     return FileResponse(
#         tempfile.name,
#         headers=headers,
#         media_type="application/json",
#         background=BackgroundTask(tempfile.close),
#     )


# @router.get("/types", status_code=status.HTTP_200_OK)
# async def map_layer_types() -> dict:
#     """Returns a list of all available data layer unit types"""
#     resp_data = {}
#     for lt_name, lt_type in get_layer_types().items():
#         resp_data[lt_name] = {
#             "name": lt_type.get_name(),
#             "description": lt_type.get_description(),
#         }
#     return resp_data


@router.get("/{layer_id}", status_code=status.HTTP_200_OK)
async def get_layer(
    layer_id: str,
) -> dict:
    layer = await LayerBase.get(layer_id, with_children=True)
    if not layer:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No layer with ID {layer_id}"
        )
    # here we're not returning data using our models, as this endpoint works for
    # any layer type - thus we have to "translate" the response a bit...
    return from_mongo(layer)
